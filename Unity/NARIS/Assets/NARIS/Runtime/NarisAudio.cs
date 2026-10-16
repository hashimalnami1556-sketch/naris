using System.Collections.Generic;
using UnityEngine;
namespace Naris {
public sealed class NarisAudio : MonoBehaviour {
    public static NarisAudio Instance {get;private set;}
    AudioSource source;
    readonly Dictionary<string,AudioClip> clips=new Dictionary<string,AudioClip>();
    void Awake() { Instance=this;source=gameObject.AddComponent<AudioSource>();source.spatialBlend=0; }
    public static void Play(string key,float volume=.45f) {
        if(!Instance)return;
        if(!Instance.clips.TryGetValue(key,out var clip)) {
            clip=Resources.Load<AudioClip>("Audio/"+key);Instance.clips[key]=clip;
        }
        if(clip)Instance.source.PlayOneShot(clip,volume);
    }
    void OnDestroy(){if(Instance==this)Instance=null;}
}
}
