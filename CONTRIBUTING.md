# contributing to yettagam

yettagam is an open schema ecosystem. we welcome contributions of new yType definitions from anyone. this guide explains how to create and submit a new type.

## repository structure

```
yettagam-net-website/
  app.yaml                              # app engine configuration
  main.py                               # WSGI 404 handler
  requirements.txt                      # python dependencies (empty)
  index.html                            # landing page
  404.html                              # error page
  schemas/
    index.html                          # interactive schema browser
  integration/
    index.html                          # integration guide
  static/
    css/style.css                       # site styling
    js/schema-browser.js                # schema browser logic
    logos/favicon.svg                    # favicon
  ytype/
    1.0.0/
      schema.json                       # yType meta-schema (layer 1)
  ytype_template/
    1.0.0/
      schema.json                       # yObj template schema (layer 3)
  ytypes/
    index.json                          # type manifest (all types listed here)
    base/
      1.0.0/base.ytype                  # versioned permalink (immutable)
      latest.ytype                      # convenience copy (mutable)
    image/
      1.0.0/image.ytype
      latest.ytype
    ...                                 # one directory per type
  agent-context/
    index.json                          # machine-readable context for AI agents
```

## how to contribute a new yType

### 1. understand the type hierarchy

yettagam types form an inheritance tree. every type inherits from at least one parent (except `base`, which is the root). browse the current hierarchy at [yettagam.net/schemas/](https://yettagam.net/schemas/).

```
base (abstract)
  +-- ibase (abstract)
  |   +-- imedia (abstract)
  |       +-- image
  +-- media (abstract)
  |   +-- audio
  |   +-- video
  |   +-- document
  +-- commit
  +-- exhibition
  +-- list
  +-- venue
  +-- vr_device
  +-- url
  +-- platform_specific (abstract)
      +-- x_tweet
      +-- youtube_video
```

decide which existing type your new type should inherit from. most concrete types inherit from `base` or one of the abstract types like `media`, `imedia`, or `platform_specific`.

### 2. create your .ytype file

create a JSON file following the meta-schema at [yettagam.net/ytype/1.0.0/schema.json](https://yettagam.net/ytype/1.0.0/schema.json).

here is a minimal template:

```json
{
  "$schema": "https://yettagam.net/ytype/1.0.0/schema.json",
  "$version": "1.0.0",
  "$role": "type-definition",
  "name": "my-type",
  "label": "My Type",
  "description": "a brief description of what this type represents",
  "kind": "concrete",
  "final": false,
  "singleton": false,
  "inherits_from": ["/ytypes/base/"],
  "definition": {
    "predicateGroups": {}
  },
  "schema": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "unique identifier for this object"
      },
      "label": {
        "type": "string",
        "description": "human-readable display name"
      },
      "description": {
        "type": "string",
        "description": "brief description of this object"
      },
      "my_custom_field": {
        "type": "string",
        "description": "a field specific to this type"
      }
    },
    "required": ["name", "label", "description", "my_custom_field"]
  }
}
```

### required top-level fields

| field | type | description |
|-------|------|-------------|
| `$schema` | string | must be `"https://yettagam.net/ytype/1.0.0/schema.json"` |
| `$version` | string | semver version of your type (start with `"1.0.0"`) |
| `$role` | string | must be `"type-definition"` |
| `name` | string | lowercase, alphanumeric + underscores (e.g., `"my_type"`) |
| `label` | string | human-readable name (e.g., `"My Type"`) |
| `description` | string | brief description of the type |
| `kind` | string | `"abstract"` or `"concrete"` — abstract types cannot be instantiated directly |
| `final` | boolean | if `true`, no other type can inherit from this one |
| `singleton` | boolean | if `true`, only one instance of this type can exist |
| `inherits_from` | array | list of parent type paths (e.g., `["/ytypes/base/"]`) |
| `definition` | object | type metadata including predicate groups |
| `schema` | object | JSON Schema defining what instances of this type look like |

### naming conventions

- **type name**: lowercase, alphanumeric, underscores only. must match the filename (e.g., `my_type` -> `my_type.ytype`)
- **label**: title case, human-readable
- **description**: lowercase, brief, starts without an article

### 3. add predicate groups (optional)

predicate groups define semantic relationships for your type. they go in `definition.predicateGroups`:

```json
{
  "definition": {
    "predicateGroups": {
      "spatial": {
        "label": "Spatial Relationships",
        "description": "relationships describing physical location and space",
        "predicates": {
          "locatedAt": {
            "description": "the physical location of this object",
            "symmetric": false,
            "transitive": false
          },
          "nearTo": {
            "description": "proximity to another object",
            "symmetric": true,
            "transitive": false
          }
        }
      }
    }
  }
}
```

look at existing types like [commit](https://yettagam.net/ytypes/commit/latest.ytype) or [image](https://yettagam.net/ytypes/image/latest.ytype) for examples of predicate group structures.

### 4. validate your type

before submitting, validate your `.ytype` file:

- ensure it is valid JSON (use `python3 -m json.tool my_type.ytype`)
- verify all required top-level fields are present
- verify `$schema` points to `https://yettagam.net/ytype/1.0.0/schema.json`
- verify `inherits_from` references an existing type (e.g., `"/ytypes/base/"`)
- verify `schema.type` is `"object"` and `schema.properties` is defined
- if you have nested object properties with required fields, put `required` arrays inside the nested object schema (not as dotted names in the top-level `required`)

### 5. prepare your pull request

fork the repository and create a branch:

```bash
git clone https://github.com/MetariumProject/yettagam-net-website.git
cd yettagam-net-website
git checkout -b add-type/my-type
```

add your files following this structure:

```
ytypes/
  my_type/
    1.0.0/
      my_type.ytype       # your type definition
    latest.ytype           # identical copy of the versioned file
```

```bash
mkdir -p ytypes/my_type/1.0.0
cp my_type.ytype ytypes/my_type/1.0.0/my_type.ytype
cp my_type.ytype ytypes/my_type/latest.ytype
```

### 6. update the type manifest

add your type to `ytypes/index.json` in the `types` array (keep alphabetical order):

```json
{
  "name": "my_type",
  "label": "My Type",
  "description": "a brief description of what this type represents",
  "kind": "concrete",
  "version": "1.0.0",
  "final": false,
  "singleton": false,
  "inherits_from": ["/ytypes/base/"],
  "permalink": "https://yettagam.net/ytypes/my_type/1.0.0/my_type.ytype",
  "latest": "https://yettagam.net/ytypes/my_type/latest.ytype"
}
```

### 7. submit your pull request

commit and push:

```bash
git add ytypes/my_type/ ytypes/index.json
git commit -m "feat: add my_type yType definition"
git push origin add-type/my-type
```

open a pull request against `main` on [github.com/MetariumProject/yettagam-net-website](https://github.com/MetariumProject/yettagam-net-website).

**in your PR description, include:**
- what the type represents and why it is needed
- which parent type it inherits from and why
- example use cases for the type
- any predicate groups you defined and their purpose

### 8. review process

a maintainer will review your PR and check:
- the `.ytype` file validates against the meta-schema
- the type name and structure follow conventions
- the inheritance choice makes sense
- the `schema` section properly defines instance properties
- `ytypes/index.json` is correctly updated
- both versioned and `latest.ytype` files are present and identical

## updating an existing type

to update an existing type to a new version:

1. create a new versioned directory: `ytypes/{name}/{new_version}/{name}.ytype`
2. update `$version` in the file to the new version
3. update `latest.ytype` to match the new version
4. update the `version` and `permalink` in `ytypes/index.json`
5. keep the old version directory in place (versioned URLs are immutable permalinks)

## questions?

- browse existing types at [yettagam.net/schemas/](https://yettagam.net/schemas/)
- read the [integration guide](https://yettagam.net/integration/) for schema details
- open an issue on [github](https://github.com/MetariumProject/yettagam-net-website/issues)

## license

all contributions are licensed under the [Apache License 2.0](LICENSE).
