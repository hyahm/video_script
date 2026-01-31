# 数据导图

### Loopftp
```json
```
 ↓

```json
{
    "ftp_dir": "/test",
    "name": "json's filename",
    "user": "test",
    "filename": "video full filename",
    "identifier": "identifier"
}

```

### Downloader

```json
{
    "ftp_dir": "/test",
    "name": "json's filename",
    "user": "test",
    "filename": "video full filename",
    "identifier": "identifier"
}
```
 ↓

```json
{
	"identifier": "gc_TXXjaTQNT",
	"video": {
		"title": "xxxxx",
		"cat": "xxx",
		"subcat": "xxxx",
		"actor": ""
	},
	"filename": "gc_TXXjaTQNT.mp4",
	"rule": "mm_online_mp4",
	"postparam": {
		"duration": 0,
		"play_url": "",
		"download_url": "",
		"thumb_longview": "",
		"thumbnail": "",
		"thumb_ver": "",
		"thumb_hor": "",
		"thumb_series": [],
		"cover": "maomi/gc_TXXjaTQNT.jpg",
		"webp_count": "",
		"webp": ""
	},
	"overwrite": true,
	"user": "maomi",
	"name": "gc_TXXjaTQNT"
}

```
### Pool

```json
{
	"identifier": "gc_TXXjaTQNT",
	"video": {
		"title": "xxxxx",
		"cat": "5555",
		"subcat": "hh444",
		"actor": ""
	},
	"filename": "gc_TXXjaTQNT.mp4",
	"rule": "mm_online_mp4",
	"overwrite": true,
	"user": "maomi",
	"name": "gc_TXXjaTQNT",
    "pool": true
}
```
 ↓
```json
{
	"identifier": "gc_TXXjaTQNT",
	"video": {
		"title": "mmmmmmmm",
		"cat": "66666",
		"subcat": "hh44",
		"actor": ""
	},
	"filename": "gc_TXXjaTQNT.mp4",
	"rule": "mm_online_mp4",
	"postparam": {
		"duration": 0,
		"play_url": "",
		"download_url": "",
		"thumb_longview": "",
		"thumbnail": "",
		"thumb_ver": "",
		"thumb_hor": "",
		"thumb_series": [],
		"cover": "maomi/gc_TXXjaTQNT.jpg",
		"webp_count": "",
		"webp": ""
	},
	"overwrite": true,
	"user": "maomi",
	"name": "gc_TXXjaTQNT"
    "pool": true  // 这个类似downloading功能， 防止重复， 处理完后才删除ftp
}

```
### Resource

```json
{
	"identifier": "gc_TXXjaTQNT",
	"video": {
		"title": "xxxxx",
		"cat": "xxx",
		"subcat": "xxxx",
		"actor": ""
	},
	"filename": "gc_TXXjaTQNT.mp4",
	"rule": "mm_online_mp4",
	"postparam": {
		"duration": 0,
		"play_url": "",
		"download_url": "",
		"thumb_longview": "",
		"thumbnail": "",
		"thumb_ver": "",
		"thumb_hor": "",
		"thumb_series": [],
		"cover": "maomi/gc_TXXjaTQNT.jpg",
		"webp_count": "",
		"webp": ""
	},
	"overwrite": true,
	"user": "maomi",
	"name": "gc_TXXjaTQNT"
    "pool": true  // 这个类似downloading功能， 防止重复， 处理完后才删除ftp
}
```
 ↓  // 主要为了生成缩略图
```json
{
	"identifier": "ny_QnNdhhXY",
	"video": {
		"title": "aaaaa",
		"cat": "xxxxxx",
		"subcat": "xxxxx",
		"actor": "xxxxxx"
	},
	"filename": "ny_QnNdhhXY.mp4",
	"rule": "mm_online_mp4",
	"postparam": {
		"duration": 0,
		"play_url": "",
		"download_url": "",
		"thumb_longview": "http://xxxx/resource/xxxx.jpg",
		"thumbnail": "http://xxxx/resource/xxxx.jpg",
		"thumb_ver": "http://xxxx/resource/xxxx.jpg",
		"thumb_hor": "http://xxxx/resource/xxxx.jpg",
		"thumb_series": [3, 364, 725, 1086, 1447, 1808, 2169, 2530, 2891, 3252, 3613, 3974, 4335, 4696, 5057, 5418, 5779, 6140, 6501, 6862, 7223, 7584, 7945, 8306, 8667],
		"cover": "maomi/ny_QnNdhhXY.jpg",
		"webp_count": "",
		"webp": ""
	},
	"overwrite": false,
	"user": "maomi",
	"name": "ny_QnNdhhXY",
    "pool": true // 如果有这个值， 就不用上传到资源机器了
}

```

### Publish

```json
{
	"identifier": "ny_QnNdhhXY",
	"video": {
		"title": "aaaaa",
		"cat": "xxxxxx",
		"subcat": "xxxxx",
		"actor": "xxxxxx"
	},
	"filename": "ny_QnNdhhXY.mp4",
	"rule": "mm_online_mp4",
	"postparam": {
		"duration": 0,
		"play_url": "",
		"download_url": "",
		"thumb_longview": "http://xxxx/resource/xxxx.jpg",
		"thumbnail": "http://xxxx/resource/xxxx.jpg",
		"thumb_ver": "http://xxxx/resource/xxxx.jpg",
		"thumb_hor": "http://xxxx/resource/xxxx.jpg",
		"thumb_series": [3, 364, 725, 1086, 1447, 1808, 2169, 2530, 2891, 3252, 3613, 3974, 4335, 4696, 5057, 5418, 5779, 6140, 6501, 6862, 7223, 7584, 7945, 8306, 8667],
		"cover": "maomi/ny_QnNdhhXY.jpg",
		"webp_count": "",
		"webp": ""
	},
	"overwrite": false,
	"user": "maomi",
	"name": "ny_QnNdhhXY",
    "pool": true // 如果有这个值， 就不用上传到资源机器了
}
```
 ↓  // 主要为了生成缩略图
```json
{
	"identifier": "ny_QnNdhhXY",
	"video": {
		"title": "aaaaa",
		"cat": "xxxxxx",
		"subcat": "xxxxx",
		"actor": "xxxxxx"
	},
	"filename": "ny_QnNdhhXY.mp4",
	"rule": "mm_online_mp4",
	"postparam": {
		"duration": 9000,
		"play_url": "http://xxxx/resource/xxxx.xxx",
		"download_url": "http://xxxx/resource/xxxx.MP4",
		"thumb_longview": "http://xxxx/resource/xxxx.jpg",
		"thumbnail": "http://xxxx/resource/xxxx.jpg",
		"thumb_ver": "http://xxxx/resource/xxxx.jpg",
		"thumb_hor": "http://xxxx/resource/xxxx.jpg",
		"thumb_series": [3, 364, 725, 1086, 1447, 1808, 2169, 2530, 2891, 3252, 3613, 3974, 4335, 4696, 5057, 5418, 5779, 6140, 6501, 6862, 7223, 7584, 7945, 8306, 8667],
		"cover": "maomi/ny_QnNdhhXY.jpg",
		"webp_count": 10,
		"webp": "http://xxxx/resource/xxxxxx.webp"
	},
	"overwrite": false,
	"user": "maomi",
	"name": "ny_QnNdhhXY",
    "pool": true // 如果有这个值,那就删除pool 的key值、 否则删除downloading
}

```
