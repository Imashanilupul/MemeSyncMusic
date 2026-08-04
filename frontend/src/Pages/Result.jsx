import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

function waitForCanPlay(audioElement) {
  return new Promise((resolve, reject) => {
    const onCanPlay = () => {
      cleanup();
      resolve();
    };

    const onError = () => {
      cleanup();
      reject(new Error("Failed to load audio for export."));
    };

    const cleanup = () => {
      audioElement.removeEventListener("canplaythrough", onCanPlay);
      audioElement.removeEventListener("error", onError);
    };

    audioElement.addEventListener("canplaythrough", onCanPlay);
    audioElement.addEventListener("error", onError);
    audioElement.load();
  });
}

function loadImage(url) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.crossOrigin = "anonymous";
    image.referrerPolicy = "no-referrer";
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error(`Failed to load image: ${url}`));
    image.src = url;
  });
}

function getSlideAtTime(slides, time) {
  if (!slides.length) {
    return null;
  }

  return (
    slides.find((slide) => {
      const start = Number(slide.start) || 0;
      const end = start + (Number(slide.duration) || 0);
      return time >= start && time < end;
    }) || slides[slides.length - 1]
  );
}

function drawSlide(ctx, canvas, slide, imageMap) {
  ctx.fillStyle = "#111111";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  if (slide?.image_url && imageMap.has(slide.image_url)) {
    const image = imageMap.get(slide.image_url);
    const sourceRatio = image.width / image.height;
    const targetRatio = canvas.width / canvas.height;

    let drawWidth = canvas.width;
    let drawHeight = canvas.height;
    let drawX = 0;
    let drawY = 0;

    if (sourceRatio > targetRatio) {
      drawWidth = canvas.height * sourceRatio;
      drawX = (canvas.width - drawWidth) / 2;
    } else {
      drawHeight = canvas.width / sourceRatio;
      drawY = (canvas.height - drawHeight) / 2;
    }

    ctx.drawImage(image, drawX, drawY, drawWidth, drawHeight);
  }

  ctx.fillStyle = "rgba(0, 0, 0, 0.55)";
  ctx.fillRect(0, canvas.height - 150, canvas.width, 150);
  ctx.fillStyle = "#ffffff";
  ctx.font = "bold 42px Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(slide?.text || "", canvas.width / 2, canvas.height - 75, canvas.width - 80);
}

function getRecorderMimeType() {
  const candidates = [
    "video/webm;codecs=vp9,opus",
    "video/webm;codecs=vp8,opus",
    "video/webm",
  ];

  return candidates.find((type) => MediaRecorder.isTypeSupported(type)) || "";
}

function Result() {
  const { jobId } = useParams();

  const [workflowData, setWorkflowData] = useState(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [downloadStatus, setDownloadStatus] = useState("idle");
  const [downloadError, setDownloadError] = useState("");

  useEffect(() => {
    const raw = sessionStorage.getItem(`meme-workflow-${jobId}`);

    if (!raw) {
      return;
    }

    try {
      setWorkflowData(JSON.parse(raw));
    } catch (error) {
      console.log(error);
    }
  }, [jobId]);

  const slides = useMemo(() => {
    if (!workflowData?.slides) {
      return [];
    }

    return [...workflowData.slides].sort((a, b) => a.start - b.start);
  }, [workflowData]);

  const activeSlide = useMemo(() => {
    return getSlideAtTime(slides, currentTime);
  }, [currentTime, slides]);

  const handleDownloadVideo = async () => {
    if (!workflowData?.audio_url || !slides.length) {
      setDownloadError("Missing slideshow or audio data.");
      return;
    }

    if (typeof MediaRecorder === "undefined") {
      setDownloadError("Your browser does not support video export.");
      return;
    }

    setDownloadError("");
    setDownloadStatus("preparing");

    const canvas = document.createElement("canvas");
    canvas.width = 1280;
    canvas.height = 720;
    const ctx = canvas.getContext("2d");

    if (!ctx) {
      setDownloadStatus("idle");
      setDownloadError("Failed to initialize canvas renderer.");
      return;
    }

    try {
      const imageUrls = [...new Set(slides.map((slide) => slide.image_url).filter(Boolean))];
      const loadedImages = await Promise.all(imageUrls.map((url) => loadImage(url)));
      const imageMap = new Map(imageUrls.map((url, index) => [url, loadedImages[index]]));

      const audio = new Audio(workflowData.audio_url);
      audio.crossOrigin = "anonymous";
      audio.preload = "auto";

      await waitForCanPlay(audio);

      const canvasStream = canvas.captureStream(30);
      const mixedStream = new MediaStream(canvasStream.getVideoTracks());

      const audioStream =
        typeof audio.captureStream === "function"
          ? audio.captureStream()
          : typeof audio.mozCaptureStream === "function"
            ? audio.mozCaptureStream()
            : null;

      const audioTrack = audioStream?.getAudioTracks?.()[0];
      if (audioTrack) {
        mixedStream.addTrack(audioTrack);
      }

      const mimeType = getRecorderMimeType();
      const recorder = mimeType
        ? new MediaRecorder(mixedStream, { mimeType })
        : new MediaRecorder(mixedStream);

      const chunks = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      const stopped = new Promise((resolve) => {
        recorder.onstop = () => resolve();
      });

      const renderLoop = () => {
        const time = audio.currentTime || 0;
        const frameSlide = getSlideAtTime(slides, time);
        drawSlide(ctx, canvas, frameSlide, imageMap);
        if (!audio.paused && !audio.ended) {
          requestAnimationFrame(renderLoop);
        }
      };

      setDownloadStatus("recording");
      recorder.start(1000);
      audio.currentTime = 0;
      await audio.play();
      renderLoop();

      await new Promise((resolve) => {
        audio.onended = resolve;
      });

      recorder.stop();
      await stopped;

      const blob = new Blob(chunks, { type: recorder.mimeType || "video/webm" });
      const downloadUrl = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = downloadUrl;
      anchor.download = `${jobId}.webm`;
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
      URL.revokeObjectURL(downloadUrl);

      setDownloadStatus("done");
    } catch (error) {
      console.log(error);
      setDownloadStatus("idle");
      setDownloadError(error.message || "Failed to generate downloadable video.");
    }
  };

  if (!workflowData) {
    return (
      <div className="min-h-screen flex items-center justify-center px-6">
        <div className="max-w-xl w-full p-8 border rounded-xl shadow-lg text-center">
          <h1 className="text-2xl font-bold">No generated result found</h1>
          <p className="text-gray-600 mt-3">
            Please generate a meme slideshow first from YouTube or upload flow.
          </p>
          <Link
            to="/upload"
            className="inline-block mt-6 bg-black text-white px-5 py-3 rounded-lg"
          >
            Go to Upload
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen px-6 py-10">
      <div className="max-w-4xl mx-auto p-8 border rounded-xl shadow-lg">
        <h1 className="text-3xl font-bold text-center">
          Your Meme Slideshow is Ready 🎉
        </h1>

        <p className="text-center text-gray-600 mt-3">
          Job: <span className="text-sm">{jobId}</span>
        </p>

        <div className="mt-8">
          <audio
            controls
            className="w-full"
            src={workflowData.audio_url}
            onTimeUpdate={(event) => {
              setCurrentTime(event.currentTarget.currentTime);
            }}
          />
        </div>

        <div className="mt-4 flex justify-center">
          <button
            type="button"
            onClick={handleDownloadVideo}
            disabled={downloadStatus === "preparing" || downloadStatus === "recording"}
            className="bg-black text-white px-5 py-3 rounded-lg hover:bg-gray-800 disabled:opacity-50"
          >
            {downloadStatus === "preparing"
              ? "Preparing video..."
              : downloadStatus === "recording"
                ? "Recording video..."
                : "Download Generated Video"}
          </button>
        </div>

        {downloadStatus === "done" && (
          <p className="mt-3 text-center text-green-700">
            Video download started successfully.
          </p>
        )}

        {downloadError && (
          <p className="mt-3 text-center text-red-700">
            {downloadError}
          </p>
        )}

        <div className="mt-8 border rounded-lg p-4">
          <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden flex items-center justify-center">
            {activeSlide?.image_url ? (
              <img
                src={activeSlide.image_url}
                alt="Matched meme"
                className="w-full h-full object-cover"
              />
            ) : (
              <p className="text-gray-500">No meme image available</p>
            )}
          </div>

          <div className="mt-4 text-center">
            <p className="text-lg font-semibold">
              {activeSlide?.text || "Waiting for playback..."}
            </p>
          </div>
        </div>

        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-3">Timeline</h2>
          <div className="max-h-64 overflow-auto border rounded-lg">
            {slides.map((slide, index) => (
              <div
                key={`${slide.start}-${index}`}
                className={`p-3 border-b ${
                  activeSlide === slide ? "bg-gray-100" : ""
                }`}
              >
                <p className="text-sm text-gray-500">
                  {Number(slide.start).toFixed(2)}s -{" "}
                  {(Number(slide.start) + Number(slide.duration)).toFixed(2)}s
                </p>
                <p>{slide.text}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Result;
