# Youtube-DL Transcode Pipeline

## About

This python module is designed to be run within a containerised environment and facilitates in downloading video & audio assets in S3, merging with FFMpeg and then uploading to a NAS.

### Prerequisites

> 1 - NAS storage should be mounted/bound to /workspace-output. After transcoding, the output files are simply moved to this folder, not uploaded to an endpoint

> 2 - Files are downloaded to a folder at <module_root>/workspace (not created in app, so required prior to running)

> 2 - Currently the FFMpeg transcode function will simply merge the video/audio files in to an mp4 container. Future work will include a config to apply FFMpeg functions to the assets

> 3 - This relies on a DynamoDB to track and provide the module with active jobs requiring work

> 4 - The video/audio assets are streamed to S3 via a lambda function found at [github.com/pixelventures/youtube-dl-lambda](https://github.com/pixelventures/youtube-dl-lambda)

> 5 - AWS Credentials should either be passed in via a mounted folder to /root/.aws or as ENV variables

### Running the App

The app is currently setup as a python module, to run use:

```python
python -m transcoder_pipeline
```

Docker build

```bash
docker build -t ytdl-transcoder .
```

Running in Docker
```
docker run -d \
--name ytdl-transcoder \
--mount type=bind,source=/Users/<me>/.aws,target=/root/.aws,readonly \
--mount type=bind,source=/Users/<me>/movies,target=/workspace-output \
ytdl-transcoder:latest
```

### ToDo

- Add tests
- Add docs
- Configure K8s deployment