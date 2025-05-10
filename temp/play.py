def process_files_with_rpdx(self):
    from configUtils import configModifier

    row_count = self.file_table.rowCount()

    for row in range(row_count):
        inputFilePath_item = self.file_table.item(row, 1)  # File Path column
        fileName_item = self.file_table.item(row, 0)       # File Name column

        if inputFilePath_item and fileName_item:
            inputFilePath = inputFilePath_item.text()
            fileName = fileName_item.text()

            # Step 2: Create "dirlod" directory if it doesn't exist
            dirlod_path = os.path.join(inputFilePath, "dirlod")
            os.makedirs(dirlod_path, exist_ok=True)

            # Step 3: Create directory with file name inside "dirlod"
            full_outputFilePath = os.path.join(dirlod_path, fileName)
            os.makedirs(full_outputFilePath, exist_ok=True)

            # Step 4: Create subdirectories
            subdirs = ['glb', 'gltf', 'obj', 'fbx', 'usdz']
            for sub in subdirs:
                os.makedirs(os.path.join(full_outputFilePath, sub), exist_ok=True)

            # Step 5: Define output paths
            outputFilePathGlb = os.path.join(full_outputFilePath, "glb")
            outputFilePathGltf = os.path.join(full_outputFilePath, "gltf")
            outputFilePathObj = os.path.join(full_outputFilePath, "obj")
            outputFilePathFbx = os.path.join(full_outputFilePath, "fbx")
            outputFilePathUsdz = os.path.join(full_outputFilePath, "usdz")

            # Step 6-10: JSON config paths
            InputUserCustomConfigRPDXJsonPath = os.path.join(full_outputFilePath, "UserCustomConfigRPDX.Json")
            InputUserCustomConfigRPDXJsonGLTFPath = os.path.join(full_outputFilePath, "UserCustomConfigRPDX_gltf.Json")
            InputUserCustomConfigRPDXJsonOBJPath = os.path.join(full_outputFilePath, "UserCustomConfigRPDX_obj.Json")
            InputUserCustomConfigRPDXJsonFBXPath = os.path.join(full_outputFilePath, "UserCustomConfigRPDX_fbx.Json")
            InputUserCustomConfigRPDXJsonUSDZPath = os.path.join(full_outputFilePath, "UserCustomConfigRPDX_usdz.Json")

            # Step 11: Create configModifier instance
            modifier = configModifier(
                Flattening_mode="byOpacity",
                Compact_splitMode="byOpacity",
                BakeResolution=2048,
                baseMapFormat="png",
                JsonOutputPath=full_outputFilePath
            )

            # Step 12 & 13: Modify schema and log output
            result = modifier.modify_schema()
            if result is not None:
                modified_json, export_json = result
                print("Modified Schema :")
                print(modified_json)
                print("Export Json :")
                print(export_json)
            else:
                print("Json structure was not generated due to undefined structure")
                continue

            # Step 14: Generate .bat file
            bat_content = f'rpdx -i "{full_outputFilePath}" ' \
                          f'--read_config "{InputUserCustomConfigRPDXJsonPath}" -e "{outputFilePathGlb}" ' \
                          f'--read_config "{InputUserCustomConfigRPDXJsonGLTFPath}" -e "{outputFilePathGltf}" ' \
                          f'--read_config "{InputUserCustomConfigRPDXJsonOBJPath}" -e "{outputFilePathObj}" ' \
                          f'--read_config "{InputUserCustomConfigRPDXJsonFBXPath}" -e "{outputFilePathFbx}" -r'

            bat_file_path = os.path.join(full_outputFilePath, f"{fileName}_convert.bat")
            with open(bat_file_path, 'w') as bat_file:
                bat_file.write(bat_content)

            # Step 15: Execute the .bat file
            os.system(f'"{bat_file_path}"')

            # Step 16: Print the rpdx command
            print(bat_content)
