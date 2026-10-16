using UnityEditor;
using UnityEngine;
namespace Naris.Editor {
public sealed class NarisModelImporter : AssetPostprocessor {
    void OnPreprocessModel() {
        if(!assetPath.StartsWith("Assets/NARIS/Resources/Models/")) return;
        var importer=(ModelImporter)assetImporter;
        importer.animationType=ModelImporterAnimationType.Legacy;
        importer.importAnimation=true;
        importer.animationCompression=ModelImporterAnimationCompression.Off;
        importer.addCollider=false;
        importer.isReadable=false;
        importer.importCameras=false;
        importer.importLights=false;
        importer.materialImportMode=ModelImporterMaterialImportMode.ImportStandard;
    }
}
}
