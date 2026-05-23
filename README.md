# yettagam.net

yettagam is a digital safe storage box — a coinage of "yettu" + "pettagam". in tamil, "yettu" means "8" (the number eight) and "pettagam" means "box". the shape of 8, like on a calculator display, can represent all digits — a reference to completeness and versatility. it is a set of JSON schemas (yType) that can be instantiated into objects (yObj). when saying yObj or yType, the "y" is silent.

part of the [metarium.net](https://metarium.net) ecosystem, maintained by [onemai foundation](https://onemai.net), author [metakovan](https://metakovan.net).

## schema architecture

yettagam schemas are organized into three layers:

1. **yType meta-schema** (`/ytype/1.0.0/schema.json`) — defines what a valid yType looks like
2. **yType definitions** (17 types as `.ytype` files) — each validated by the meta-schema, containing a `schema` section for validating instances
3. **yObj template** (`/ytype_template/1.0.0/schema.json`) — template for object instances validated against their respective yType

## schema URLs

every type follows a consistent URL pattern:

```
https://yettagam.net/ytypes/{name}/{version}/{name}.ytype   # immutable permalink
https://yettagam.net/ytypes/{name}/latest.ytype              # mutable, latest version
https://yettagam.net/ytypes/{name}/                          # alias for latest.ytype
```

browse all types at [yettagam.net/schemas/](https://yettagam.net/schemas/) or see the [integration guide](https://yettagam.net/integration/) for full details.

## contributing

yettagam is an open schema ecosystem. we welcome new yType definitions from anyone. see [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide on how to create and submit a new type via pull request.

## deployment

```bash
gcloud app deploy --project=yetttagam-net
```

## license

licensed under the [Apache License 2.0](LICENSE). copyright 2025 onemai foundation.
