#!/usr/bin/env python3
"""
face_anchor_usdz.py  -  wrap a USDZ model in an AR Quick Look *face* anchor.

Install:   pip install usd-core
Usage:     python3 face_anchor_usdz.py my_sunglasses.usdz out.usdz
           python3 face_anchor_usdz.py in.usdz out.usdz --width-m 0.145 --pos 0 0.025 0.065
           python3 face_anchor_usdz.py in.usdz out.usdz --rotate 0 180 0     # model faces backwards

Hierarchy written:
    /FaceAnchor            (Xform, default prim, Preliminary_AnchoringAPI, type = "face")
      /Offset              (Xform, translate / rotate / scale you control, in METERS)
        /Model             (Xform, references your original model; unit + up-axis fix applied here)

Face-space (ARKit face anchor): origin ~ centre of head, +X toward the person's
left side of the image, +Y up, +Z out of the face. Units: meters.
"""
import argparse
import os
import shutil
import sys
import tempfile
import zipfile

from pxr import Gf, Sdf, Usd, UsdGeom, UsdUtils

LAYER_EXTS = (".usdc", ".usda", ".usd")


def find_root_layer(names):
    if names and names[0].lower().endswith(LAYER_EXTS):
        return names[0]
    for n in names:
        if n.lower().endswith(LAYER_EXTS):
            return n
    raise RuntimeError("No USD layer found inside the USDZ.")


def pick_model_prim(stage):
    dp = stage.GetDefaultPrim()
    if dp:
        return dp.GetPath()
    skip = {"materials", "looks", "shaders"}
    for p in stage.GetPseudoRoot().GetChildren():
        if p.GetName().lower() not in skip and p.IsA(UsdGeom.Xformable):
            return p.GetPath()
    raise RuntimeError("Could not find a model prim (no defaultPrim set).")


def rot_matrix(deg_xyz):
    """Row-vector (Gf) matrix equivalent of USD rotateXYZ."""
    rx = Gf.Matrix4d(1).SetRotate(Gf.Rotation(Gf.Vec3d(1, 0, 0), deg_xyz[0]))
    ry = Gf.Matrix4d(1).SetRotate(Gf.Rotation(Gf.Vec3d(0, 1, 0), deg_xyz[1]))
    rz = Gf.Matrix4d(1).SetRotate(Gf.Rotation(Gf.Vec3d(0, 0, 1), deg_xyz[2]))
    return rx * ry * rz


def world_range(stage, path):
    cache = UsdGeom.BBoxCache(
        Usd.TimeCode.Default(),
        [UsdGeom.Tokens.default_, UsdGeom.Tokens.render],
        useExtentsHint=False,
    )
    r = cache.ComputeWorldBound(stage.GetPrimAtPath(path)).ComputeAlignedRange()
    if r.IsEmpty():
        raise RuntimeError("Model bounding box is empty (no geometry found).")
    return r


def build(src, dst, pos, rotate, width_m, pivot, style):
    work = tempfile.mkdtemp(prefix="faceanchor_")
    try:
        # 1. Unpack the source usdz so textures stay beside the layer.
        src_dir = os.path.join(work, "src")
        with zipfile.ZipFile(src) as z:
            z.extractall(src_dir)
            root_name = find_root_layer(z.namelist())
        src_layer = os.path.join(src_dir, root_name)
        src_stage = Usd.Stage.Open(src_layer)
        if not src_stage:
            raise RuntimeError("Could not open source layer: " + src_layer)

        src_mpu = UsdGeom.GetStageMetersPerUnit(src_stage) or 1.0
        src_up = UsdGeom.GetStageUpAxis(src_stage)
        model_path = pick_model_prim(src_stage)
        n_roots = len(src_stage.GetPseudoRoot().GetChildren())
        if n_roots > 1:
            print(f"WARNING: source has {n_roots} root prims; only {model_path} is "
                  "referenced. If materials live outside it they will be lost.")
        print(f"Source: mpu={src_mpu}, up={src_up}, model prim={model_path}")

        # 2. Wrapper stage: meters, Y-up.
        wrap_path = os.path.join(work, "face_wrapper.usda")
        w = Usd.Stage.CreateNew(wrap_path)
        UsdGeom.SetStageUpAxis(w, UsdGeom.Tokens.y)
        UsdGeom.SetStageMetersPerUnit(w, 1.0)

        if style == "rc":
            # Mimics the layout Reality Composer exports: Root / Scenes / Scene,
            # with the anchoring token on the Scene prim.
            root = UsdGeom.Xform.Define(w, "/Root")
            w.SetDefaultPrim(root.GetPrim())
            scenes = w.DefinePrim("/Root/Scenes", "Scope")
            scenes.SetMetadata("kind", "sceneLibrary")
            scene = UsdGeom.Xform.Define(w, "/Root/Scenes/Scene")
            ap = scene.GetPrim()
            ap.SetCustomDataByKey("sceneName", "Scene")
            ap.SetCustomDataByKey("preliminary_collidesWithEnvironment", False)
            ap.CreateAttribute("preliminary:anchoring:type",
                               Sdf.ValueTypeNames.Token).Set("face")
            base = "/Root/Scenes/Scene"
        else:
            anchor = UsdGeom.Xform.Define(w, "/FaceAnchor")
            w.SetDefaultPrim(anchor.GetPrim())
            ap = anchor.GetPrim()
            ap.SetMetadata("apiSchemas",
                           Sdf.TokenListOp.Create(prependedItems=["Preliminary_AnchoringAPI"]))
            ap.CreateAttribute("preliminary:anchoring:type", Sdf.ValueTypeNames.Token,
                               False, Sdf.VariabilityUniform).Set("face")
            base = "/FaceAnchor"
        anchor_path = ap.GetPath()
        offset_path = base + "/Offset"
        model_path_w = offset_path + "/Model"

        offset = UsdGeom.Xform.Define(w, offset_path)
        t_op = offset.AddTranslateOp()
        r_op = offset.AddRotateXYZOp()
        s_op = offset.AddScaleOp()
        t_op.Set(Gf.Vec3d(0, 0, 0))
        r_op.Set(Gf.Vec3f(*rotate))
        s_op.Set(Gf.Vec3f(1, 1, 1))

        # Model prim only holds the reference + unit/up-axis correction, so the
        # original root transform (inside the reference) is never overwritten.
        model = UsdGeom.Xform.Define(w, model_path_w)
        rel = os.path.relpath(src_layer, work).replace(os.sep, "/")
        refs = model.GetPrim().GetReferences()
        if src_stage.GetDefaultPrim():
            refs.AddReference("./" + rel)
        else:
            refs.AddReference("./" + rel, model_path)
        model.AddScaleOp().Set(Gf.Vec3f(src_mpu, src_mpu, src_mpu))
        if src_up == UsdGeom.Tokens.z:
            model.AddRotateXOp().Set(-90.0)

        # 3. Optional resize to a real-world frame width (meters).
        scale = 1.0
        if width_m:
            r0 = world_range(w, model_path_w)
            # width measured after user rotation, along X
            cur_w = r0.GetMax()[0] - r0.GetMin()[0]
            if cur_w <= 0:
                raise RuntimeError("Zero-width model.")
            scale = width_m / cur_w
            s_op.Set(Gf.Vec3f(scale, scale, scale))

        # 4. Place the chosen pivot of the (rotated, scaled) model at `pos`.
        r1 = world_range(w, model_path_w)
        mid = r1.GetMidpoint()
        if pivot == "front":
            p = Gf.Vec3d(mid[0], mid[1], r1.GetMax()[2])
        else:
            p = Gf.Vec3d(mid[0], mid[1], mid[2])
        t_op.Set(Gf.Vec3d(*pos) - p)

        final = world_range(w, model_path_w)
        size = final.GetMax() - final.GetMin()
        print(f"Final size (m): W={size[0]:.3f}  H={size[1]:.3f}  D={size[2]:.3f}  "
              f"(scale applied: {scale:.4f})")
        if not (0.10 <= size[0] <= 0.20):
            print("WARNING: width is outside the typical 10-20 cm range for glasses. "
                  "Pass --width-m 0.145 to force a realistic size.")

        w.GetRootLayer().Save()

        # 5. Package properly (textures included, ARKit-compliant usdz).
        if os.path.exists(dst):
            os.remove(dst)
        ok = UsdUtils.CreateNewARKitUsdzPackage(Sdf.AssetPath(wrap_path), dst)
        if not ok or not os.path.exists(dst):
            raise RuntimeError("CreateNewARKitUsdzPackage failed.")

        # 6. Verify the output.
        with zipfile.ZipFile(dst) as z:
            names = z.namelist()
        print(f"Packaged {len(names)} files:")
        for n in names:
            print("   ", n)
        out = Usd.Stage.Open(dst)
        dp = out.GetDefaultPrim()
        ap_out = out.GetPrimAtPath(anchor_path)
        print("Default prim:", dp.GetPath() if dp else "NONE (bad)")
        print("Anchor prim :", anchor_path)
        print("apiSchemas  :", ap_out.GetMetadata("apiSchemas"))
        print("anchor type :", ap_out.GetAttribute("preliminary:anchoring:type").Get())
        print(f"\nSaved: {dst}")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--pos", nargs=3, type=float, default=[0.0, 0.025, 0.065],
                    metavar=("X", "Y", "Z"),
                    help="where the pivot sits in face space, meters (starting guess; tune on device)")
    ap.add_argument("--rotate", nargs=3, type=float, default=[0.0, 0.0, 0.0],
                    metavar=("RX", "RY", "RZ"), help="degrees; model's front must end up facing +Z")
    ap.add_argument("--width-m", type=float, default=None,
                    help="resize so overall width equals this many meters (e.g. 0.145)")
    ap.add_argument("--pivot", choices=["front", "center"], default="front",
                    help="front = centre of the front plane (best for glasses with arms)")
    ap.add_argument("--style", choices=["rc", "api"], default="rc",
                    help="rc = Reality Composer-style Root/Scenes/Scene layout (default); "
                         "api = anchor on default prim via Preliminary_AnchoringAPI")
    a = ap.parse_args()
    if not os.path.exists(a.src):
        sys.exit("Input not found: " + a.src)
    build(a.src, a.dst, a.pos, a.rotate, a.width_m, a.pivot, a.style)


if __name__ == "__main__":
    main()
