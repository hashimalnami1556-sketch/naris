using System;
using System.IO;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
namespace Naris.Editor {
public static class BuildNaris {
    [MenuItem("NARIS/Prepare Ash Gate")]
    public static void Prepare() {
        Directory.CreateDirectory("Assets/NARIS/Art");
        Directory.CreateDirectory("Assets/NARIS/Scenes");
        var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        var world=new GameObject("NARIS - Ash Gate").AddComponent<WorldBootstrap>();
        world.stone=Material("Basalt",new Color(.16f,.19f,.22f));
        world.ground=Material("Ash",new Color(.22f,.23f,.24f));
        world.ember=Material("Ember",new Color(1,.31f,.04f));
        world.teal=Material("Vessel",new Color(.1f,.65f,.7f));
        EditorSceneManager.SaveScene(scene,"Assets/NARIS/Scenes/AshGate.unity");
        EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene("Assets/NARIS/Scenes/AshGate.unity",true)};
        PlayerSettings.companyName="ALNAMI";
        PlayerSettings.productName="NARIS";
        PlayerSettings.bundleVersion="0.2.0";
        PlayerSettings.defaultIsNativeResolution=false;
        PlayerSettings.defaultScreenWidth=1280; PlayerSettings.defaultScreenHeight=720;
        PlayerSettings.fullScreenMode=FullScreenMode.Windowed;
        PlayerSettings.runInBackground=true;
        AssetDatabase.SaveAssets();
    }
    static Material Material(string name,Color color) {
        string path="Assets/NARIS/Art/"+name+".mat";
        var material=AssetDatabase.LoadAssetAtPath<Material>(path);
        if(!material) { material=new Material(Shader.Find("Standard")); AssetDatabase.CreateAsset(material,path); }
        material.color=color; return material;
    }
    [MenuItem("NARIS/Build Windows")]
    public static void BuildWindows() => BuildTargetPlayer(BuildTarget.StandaloneWindows64,"Windows/NARIS.exe");
    [MenuItem("NARIS/Build Linux")]
    public static void BuildLinux() => BuildTargetPlayer(BuildTarget.StandaloneLinux64,"Linux/NARIS.x86_64");
    [MenuItem("NARIS/Build macOS")]
    public static void BuildMac() => BuildTargetPlayer(BuildTarget.StandaloneOSX,"macOS/NARIS.app");
    [MenuItem("NARIS/Build WebGL")]
    public static void BuildWebGL() => BuildTargetPlayer(BuildTarget.WebGL,"WebGL");
    static void BuildTargetPlayer(BuildTarget target,string relativeOutput) {
        NarisAssetValidation.Validate();
        Prepare();
        string root=Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
        string output=Path.Combine(root,"Builds",relativeOutput);
        Directory.CreateDirectory(Path.GetDirectoryName(output));
        var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions {
            scenes=new[]{"Assets/NARIS/Scenes/AshGate.unity"},
            locationPathName=output,target=target,options=BuildOptions.Development
        });
        string summary="Result: "+report.summary.result+"; target: "+target+"; errors: "+report.summary.totalErrors+"; bytes: "+report.summary.totalSize;
        Directory.CreateDirectory(Path.Combine(root,"Reports"));
        File.WriteAllText(Path.Combine(root,"Reports","build-"+target+".txt"),summary);
        if(report.summary.result!=BuildResult.Succeeded) throw new Exception(summary);
        Debug.Log("NARIS_BUILD_PASS "+summary);
    }
}
}
