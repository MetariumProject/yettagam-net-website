# yettagam.net

yettagam is a digital safe storage box — a coinage of "yettu" + "pettagam" (Tamil for box). it is a set of JSON schemas (yType) that can be instantiated into objects (yObj). when saying yObj or yType, the "y" is silent.

part of the [metarium.net](https://metarium.net) ecosystem, maintained by [onemai foundation](https://onemai.net), author [metakovan](https://metakovan.net).

## schema architecture

yettagam schemas are organized into three layers:

### layer 1: yType meta-schema

the meta-schema defines what a valid yType looks like. all 17 type definitions are validated against it.

**URL:** `/ytype/1.0.0/schema.json`

### layer 2: yType definitions (17 types)

each type definition conforms to the meta-schema and describes the structure, inheritance, and validation rules for objects of that type.

### layer 3: yObj template

the yObj template schema provides the template for object instances — the actual data objects that are validated against their respective yType's schema section.

**URL:** `/ytype_template/1.0.0/schema.json`

## schema URL reference

| type | versioned permalink | latest |
|------|-------------------|--------|
| audio | `/ytypes/audio/1.0.0/audio.ytype` | `/ytypes/audio/latest.ytype` |
| base | `/ytypes/base/1.0.0/base.ytype` | `/ytypes/base/latest.ytype` |
| commit | `/ytypes/commit/1.0.0/commit.ytype` | `/ytypes/commit/latest.ytype` |
| document | `/ytypes/document/1.0.0/document.ytype` | `/ytypes/document/latest.ytype` |
| exhibition | `/ytypes/exhibition/1.0.0/exhibition.ytype` | `/ytypes/exhibition/latest.ytype` |
| ibase | `/ytypes/ibase/1.0.0/ibase.ytype` | `/ytypes/ibase/latest.ytype` |
| image | `/ytypes/image/1.0.0/image.ytype` | `/ytypes/image/latest.ytype` |
| imedia | `/ytypes/imedia/1.0.0/imedia.ytype` | `/ytypes/imedia/latest.ytype` |
| list | `/ytypes/list/1.0.0/list.ytype` | `/ytypes/list/latest.ytype` |
| media | `/ytypes/media/1.0.0/media.ytype` | `/ytypes/media/latest.ytype` |
| platform_specific | `/ytypes/platform_specific/1.0.0/platform_specific.ytype` | `/ytypes/platform_specific/latest.ytype` |
| url | `/ytypes/url/1.0.0/url.ytype` | `/ytypes/url/latest.ytype` |
| venue | `/ytypes/venue/1.0.0/venue.ytype` | `/ytypes/venue/latest.ytype` |
| video | `/ytypes/video/1.0.0/video.ytype` | `/ytypes/video/latest.ytype` |
| vr_device | `/ytypes/vr_device/1.0.0/vr_device.ytype` | `/ytypes/vr_device/latest.ytype` |
| x_tweet | `/ytypes/x_tweet/1.0.0/x_tweet.ytype` | `/ytypes/x_tweet/latest.ytype` |
| youtube_video | `/ytypes/youtube_video/1.0.0/youtube_video.ytype` | `/ytypes/youtube_video/latest.ytype` |

## deployment

```bash
gcloud app deploy --project=yetttagam-net
```
