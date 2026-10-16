using System;
using System.Linq;
using UnityEditor;
using UnityEngine;
namespace Naris.Editor {
public static class NarisAssetValidation {
    [MenuItem("NARIS/Validate Imported Assets")]
    public static void Validate() {
        foreach(string name in new[]{"SK_AshenVessel","SK_BoneBeast","SK_CelestialWolf"}) {
            string path="Assets/NARIS/Resources/Models/"+name+".fbx";
            var model=AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if(!model || model.GetComponentsInChildren<SkinnedMeshRenderer>().Length==0)
                throw new Exception("Missing skinned model: "+path);
            var clips=AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__")).ToArray();
            if(!clips.Any(c=>c.name.Contains("Idle")) || !clips.Any(c=>c.name.Contains("Run")))
                throw new Exception("Missing idle/run animations: "+path);
            Debug.Log("NARIS_ASSET_PASS "+name+" clips="+clips.Length);
        }
        foreach(string name in new[]{"chime_01","whoosh_01","impact_01","click_01","rumble_01"}) {
            if(!AssetDatabase.LoadAssetAtPath<AudioClip>("Assets/NARIS/Resources/Audio/"+name+".wav"))
                throw new Exception("Missing audio: "+name);
        }
    }
}
}
