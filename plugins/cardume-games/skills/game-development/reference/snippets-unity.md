# Unity Snippets (C#)

Written for Unity 6 (6.3 LTS at the time of writing; check unity.com/releases for the current LTS). Assumes the Input System package: the legacy Input Manager (`UnityEngine.Input`) is deprecated and Unity says it will be removed in a future version, so use it only in legacy projects. Adapt to the project's Unity version and input setup.

## Platformer controller (kinematic-style on Rigidbody2D)

```csharp
using UnityEngine;
using UnityEngine.InputSystem;

[RequireComponent(typeof(Rigidbody2D))]
public class PlayerController : MonoBehaviour
{
    [SerializeField] float speed = 8f, accel = 80f;
    [SerializeField] float jumpHeight = 3f, timeToApex = 0.35f, fallGravityMult = 2f, jumpCut = 0.45f;
    [SerializeField] float coyoteTime = 0.1f, jumpBufferTime = 0.12f;
    [SerializeField] LayerMask groundMask;
    [SerializeField] InputActionReference move, jump;

    Rigidbody2D rb;
    float gravity, jumpVelocity, coyote, buffer;
    bool jumpReleased;

    void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
        rb.gravityScale = 0f; // we apply gravity ourselves
        gravity = 2f * jumpHeight / (timeToApex * timeToApex);
        jumpVelocity = gravity * timeToApex;
    }

    // Read input every frame so short presses are not lost between physics ticks.
    void Update()
    {
        if (jump.action.WasPressedThisFrame()) buffer = jumpBufferTime;
        if (jump.action.WasReleasedThisFrame()) jumpReleased = true;
    }

    void FixedUpdate()
    {
        float dt = Time.fixedDeltaTime;
        bool grounded = Physics2D.BoxCast(transform.position, new Vector2(0.8f, 0.1f), 0f, Vector2.down, 0.55f, groundMask);
        coyote = grounded ? coyoteTime : Mathf.Max(coyote - dt, 0f);
        buffer = Mathf.Max(buffer - dt, 0f);

        Vector2 v = rb.linearVelocity; // `velocity` in older Unity versions
        v.y -= gravity * (v.y < 0f ? fallGravityMult : 1f) * dt;

        if (buffer > 0f && coyote > 0f) { v.y = jumpVelocity; buffer = coyote = 0f; }
        if (jumpReleased && v.y > 0f) v.y *= jumpCut;
        jumpReleased = false;

        float dir = move.action.ReadValue<Vector2>().x;
        v.x = Mathf.MoveTowards(v.x, dir * speed, accel * dt);
        rb.linearVelocity = v;
    }
}
```

Set the Rigidbody2D interpolation to Interpolate for smooth rendering between fixed steps.

## ScriptableObject definition

```csharp
[CreateAssetMenu(menuName = "Game/Enemy Definition")]
public class EnemyDef : ScriptableObject
{
    public string displayName;
    public int maxHp = 10;
    public float speed = 3f;
    public Sprite sprite;
}
```

Keep runtime state (current HP) on the instance component, not in the ScriptableObject.

## Event channel

```csharp
[CreateAssetMenu(menuName = "Game/Events/Int Event")]
public class IntEvent : ScriptableObject
{
    public event System.Action<int> Raised;
    public void Raise(int value) => Raised?.Invoke(value);
}
// Subscribe in OnEnable, unsubscribe in OnDisable to avoid leaks.
```

## Pooling

```csharp
using UnityEngine.Pool;

ObjectPool<Bullet> pool = new(
    createFunc: () => Instantiate(prefab),
    actionOnGet: b => b.gameObject.SetActive(true),
    actionOnRelease: b => b.gameObject.SetActive(false),
    defaultCapacity: 64);
```

## Versioned save

```csharp
using System.IO;
using UnityEngine;

[System.Serializable] public class SaveData { public int version = 2; public int coins; public int level; }

public static void Save(SaveData d)
{
    string path = Path.Combine(Application.persistentDataPath, "save.json");
    string tmp = path + ".tmp";
    File.WriteAllText(tmp, JsonUtility.ToJson(d));
    if (File.Exists(path)) File.Replace(tmp, path, path + ".bak"); else File.Move(tmp, path);
}
```

Migrate on load by checking `version` before using fields.

## Tests and builds

- Edit Mode tests (NUnit) for pure logic; Play Mode tests for scene behavior, via the Test Framework package.
- CI: `Unity -batchmode -nographics -projectPath . -runTests -testPlatform EditMode` and `-executeMethod BuildScript.Build` for builds.
