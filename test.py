import streamlit as st
import threading
from typing import Optional
from PIL import Image as PILImage
from av import VideoFrame
from streamlit_webrtc import VideoProcessorBase, ClientSettings, \
    webrtc_streamer


def main() -> None:
    class VideoProcessor(VideoProcessorBase):
        frame_lock: threading.Lock  # `recv()` is running in another thread,
        # then a lock object is used here for thread-safety.
        out_image: Optional[PILImage.Image]

        def __init__(self) -> None:
            self.frame_lock = threading.Lock()
            self.out_image = None

        def recv(self, frame: VideoFrame) -> VideoFrame:
            in_image = frame.to_image()
            out_image = in_image.transpose(PILImage.FLIP_LEFT_RIGHT)

            with self.frame_lock:
                self.out_image = out_image

            return VideoFrame.from_image(out_image)

    ctx = webrtc_streamer(
        key="ecs171-group10",
        client_settings=ClientSettings(
            media_stream_constraints={"video": True, "audio": False},
        ),
        video_processor_factory=VideoProcessor,
    )

    if ctx.video_processor:
        if st.button("Take a picture"):
            with ctx.video_processor.frame_lock:
                out_image = ctx.video_processor.out_image

            if out_image is not None:
                st.image(out_image)

            else:
                st.warning("No frames available yet.")


main()
