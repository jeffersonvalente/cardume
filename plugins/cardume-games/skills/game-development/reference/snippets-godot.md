# Godot 4 Snippets (GDScript)

Check against the project's Godot version; APIs below follow Godot 4.x conventions (4.7.x is the current stable series at the time of writing). Since 4.6, new projects use Jolt as the default 3D physics engine (Project Settings → `physics/3d/physics_engine`); existing projects keep their setting. C# (.NET) projects in Godot 4 cannot export to the web yet per the official export docs; use GDScript for web targets.

## Platformer controller with coyote time, jump buffer and variable jump

```gdscript
extends CharacterBody2D

@export var speed := 180.0
@export var accel := 1800.0
@export var jump_height := 64.0
@export var time_to_apex := 0.35
@export var fall_gravity_mult := 2.0
@export var jump_cut := 0.45
@export var coyote_time := 0.1
@export var jump_buffer_time := 0.12

var _gravity: float
var _jump_velocity: float
var _coyote := 0.0
var _buffer := 0.0

func _ready() -> void:
    _gravity = 2.0 * jump_height / pow(time_to_apex, 2)
    _jump_velocity = -_gravity * time_to_apex

func _physics_process(delta: float) -> void:
    _coyote = coyote_time if is_on_floor() else maxf(_coyote - delta, 0.0)
    _buffer = jump_buffer_time if Input.is_action_just_pressed("jump") else maxf(_buffer - delta, 0.0)

    var g := _gravity * (fall_gravity_mult if velocity.y > 0.0 else 1.0)
    velocity.y += g * delta

    if _buffer > 0.0 and _coyote > 0.0:
        velocity.y = _jump_velocity
        _buffer = 0.0
        _coyote = 0.0
    if Input.is_action_just_released("jump") and velocity.y < 0.0:
        velocity.y *= jump_cut

    var dir := Input.get_axis("move_left", "move_right")
    velocity.x = move_toward(velocity.x, dir * speed, accel * delta)
    move_and_slide()
```

Define `jump`, `move_left`, `move_right` in Project Settings → Input Map. Enable physics interpolation in project settings for smooth rendering at high refresh rates.

## Signal-based event bus (autoload)

```gdscript
# events.gd, registered as autoload "Events"
extends Node
signal coin_collected(value: int)
signal player_died
```

```gdscript
# coin.gd (emitter): emit from inside a function, e.g. when the player touches the coin
extends Area2D

func _on_body_entered(_body: Node2D) -> void:
    Events.coin_collected.emit(10)
    queue_free()
```

```gdscript
# hud.gd (listener)
extends CanvasLayer

func _ready() -> void:
    Events.coin_collected.connect(_on_coin_collected)

func _on_coin_collected(value: int) -> void:
    pass  # update the coin label
```

## Data resource

```gdscript
class_name EnemyDef
extends Resource
@export var display_name := ""
@export var max_hp := 10
@export var speed := 60.0
@export var sprite: Texture2D
```

## Versioned save

```gdscript
const SAVE_PATH := "user://save.json"
const SAVE_VERSION := 2

func save_game(data: Dictionary) -> void:
    data["version"] = SAVE_VERSION
    var tmp := SAVE_PATH + ".tmp"
    var f := FileAccess.open(tmp, FileAccess.WRITE)
    f.store_string(JSON.stringify(data))
    f.close()
    DirAccess.rename_absolute(ProjectSettings.globalize_path(tmp), ProjectSettings.globalize_path(SAVE_PATH))

func load_game() -> Dictionary:
    if not FileAccess.file_exists(SAVE_PATH):
        return {}
    var data = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
    if typeof(data) != TYPE_DICTIONARY:
        return {}
    return _migrate(data)

func _migrate(d: Dictionary) -> Dictionary:
    if d.get("version", 1) < 2:
        d["coins"] = d.get("gold", 0)   # v1 -> v2 rename
        d.erase("gold")
        d["version"] = 2
    return d
```

## Object pool

```gdscript
var _pool: Array[Node2D] = []
@export var bullet_scene: PackedScene

func get_bullet() -> Node2D:
    var b: Node2D = _pool.pop_back() if not _pool.is_empty() else bullet_scene.instantiate()
    if b.get_parent() == null:
        add_child(b)
    b.show()
    b.set_process(true)
    return b

func release(b: Node2D) -> void:
    b.hide()
    b.set_process(false)
    _pool.append(b)
```

## Headless export and tests in CI

```bash
godot --headless --export-release "Web" build/web/index.html
godot --headless -s addons/gut/gut_cmdln.gd   # if the project uses GUT for tests
```
