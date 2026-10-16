using UnityEngine;
namespace Naris {
public sealed class ActorVisual : MonoBehaviour {
    Animation clips;
    Vector3 previous;
    string active;
    float actionUntil;
    public static bool Attach(GameObject actor,string resource,float height) {
        var prefab=Resources.Load<GameObject>("Models/"+resource);
        if(!prefab){Debug.LogError("NARIS_MODEL_MISSING: "+resource);return false;}
        var model=Instantiate(prefab,actor.transform,false); model.name="Visual - "+resource;
        var renderers=model.GetComponentsInChildren<Renderer>();
        if(renderers.Length==0){Destroy(model);return false;}
        var bounds=renderers[0].bounds; foreach(var item in renderers) bounds.Encapsulate(item.bounds);
        if(bounds.size.y<=.00001f){Destroy(model);return false;}
        model.transform.localScale*=height/bounds.size.y;
        bounds=renderers[0].bounds;foreach(var item in renderers)bounds.Encapsulate(item.bounds);
        model.transform.position+=actor.transform.position-new Vector3(bounds.center.x,bounds.min.y,bounds.center.z);
        var visual=actor.AddComponent<ActorVisual>();
        visual.clips=model.GetComponentInChildren<Animation>();
        visual.previous=actor.transform.position;
        if(visual.clips) foreach(AnimationState state in visual.clips)
            state.wrapMode=(state.name.Contains("Idle")||state.name.Contains("Walk")||state.name.Contains("Run"))?WrapMode.Loop:WrapMode.Once;
        return true;
    }
    void Update() {
        if(Time.timeScale==0)return;
        float speed=(transform.position-previous).magnitude/Mathf.Max(Time.deltaTime,.001f);
        previous=transform.position;
        if(Time.time<actionUntil)return;
        Play(speed>.4f?"Run":"Idle");
    }
    void Play(string token) {
        if(!clips)return;
        foreach(AnimationState state in clips) {
            if(!state.name.Contains(token))continue;
            if(active!=state.name){clips.CrossFade(state.name,.12f);active=state.name;}
            return;
        }
    }
    public void Action(string token,float duration) { active=null;Play(token);actionUntil=Time.time+duration; }
}
}
