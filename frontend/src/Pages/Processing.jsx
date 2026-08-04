import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import api, { getAnalysis, searchMeme } from "../Services/api";

function getNearestBeatTime(time, beatTimes) {
  if (!beatTimes.length) {
    return Number(time) || 0;
  }

  let nearest = beatTimes[0];
  let smallestDiff = Math.abs(beatTimes[0] - time);

  beatTimes.forEach((beatTime) => {
    const diff = Math.abs(beatTime - time);
    if (diff < smallestDiff) {
      smallestDiff = diff;
      nearest = beatTime;
    }
  });

  return nearest;
}

function Processing() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const jobId = searchParams.get("job");
  const source = searchParams.get("source") || "upload";
  const audioFile = searchParams.get("audioFile");

  const [progress, setProgress] = useState(5);
  const [status, setStatus] = useState("loading"); // loading | success | error
  const [stepMessage, setStepMessage] = useState("Starting workflow...");
  const [errorMessage, setErrorMessage] = useState("");

  const expectedFlow = useMemo(() => {
    if (source === "youtube") {
      return [
        "Get beat analysis from /analyze/{job_id}",
        "Load lyrics/transcript from /youtube/process output",
        "Search meme images from /meme/search for each lyric",
        "Build beat-synced slideshow timeline",
      ];
    }

    return ["Get beat analysis from /analyze/{job_id}"];
  }, [source]);

  useEffect(() => {
    if (!jobId) {
      setStatus("error");
      setErrorMessage("Missing job ID.");
      return;
    }

    let cancelled = false;

    const runWorkflow = async () => {
      try {
        setStepMessage("Analyzing beats...");
        setProgress(20);

        const analysisResponse = await getAnalysis(jobId);
        if (cancelled) {
          return;
        }

        const analysis = analysisResponse.data;
        const audioUrl =
          source === "youtube"
            ? `${import.meta.env.VITE_API_BASE_URL}/uploads/${jobId}/audio.mp3`
            : `${import.meta.env.VITE_API_BASE_URL}/uploads/${audioFile || `${jobId}.mp3`}`;

        if (source !== "youtube") {
          const fallbackResult = {
            job_id: jobId,
            source,
            analysis,
            slides: [
              {
                text: "No lyrics were provided for this upload.",
                image_url: "",
                start: 0,
                duration: analysis.duration || 3,
              },
            ],
            transcript: [],
            audio_url: audioUrl,
            generated_at: new Date().toISOString(),
          };

          sessionStorage.setItem(
            `meme-workflow-${jobId}`,
            JSON.stringify(fallbackResult)
          );

          setProgress(100);
          setStepMessage("Ready! Opening your result...");
          setStatus("success");

          setTimeout(() => {
            if (!cancelled) {
              navigate(`/result/${jobId}`);
            }
          }, 500);
          return;
        }

        setStepMessage("Loading transcript...");
        setProgress(35);

        const transcriptResponse = await api.get(`/uploads/${jobId}/transcript.json`);
        if (cancelled) {
          return;
        }

        const transcript = Array.isArray(transcriptResponse.data)
          ? transcriptResponse.data.filter((item) => item?.text?.trim())
          : [];

        if (!transcript.length) {
          throw new Error("No transcript lines were found for this YouTube video.");
        }

        const beatTimes = Array.isArray(analysis.beat_times) ? analysis.beat_times : [];
        const memeCache = new Map();
        const slides = [];

        for (let index = 0; index < transcript.length; index += 1) {
          const lyric = transcript[index];
          const normalizedText = lyric.text.trim();

          let memeResult = memeCache.get(normalizedText);
          if (!memeResult) {
            setStepMessage(`Finding meme for lyric ${index + 1}/${transcript.length}...`);
            memeResult = await searchMeme(normalizedText);
            memeCache.set(normalizedText, memeResult.data);
          }

          if (cancelled) {
            return;
          }

          const currentStart = Number(lyric.start) || 0;
          const nextStart = Number(transcript[index + 1]?.start);
          const alignedStart = getNearestBeatTime(currentStart, beatTimes);
          const alignedNextStart = Number.isFinite(nextStart)
            ? getNearestBeatTime(nextStart, beatTimes)
            : null;

          let duration = Number(lyric.duration) || 2;
          if (alignedNextStart !== null && alignedNextStart > alignedStart) {
            duration = alignedNextStart - alignedStart;
          }
          duration = Math.max(0.4, duration);

          slides.push({
            text: normalizedText,
            image_url: memeResult.data?.memes?.[0]?.url || "",
            meme_options: memeResult.data?.memes || [],
            start: alignedStart,
            duration,
          });

          const baseProgress = 35;
          const ratio = (index + 1) / transcript.length;
          setProgress(Math.min(95, Math.round(baseProgress + ratio * 55)));
        }

        const resultPayload = {
          job_id: jobId,
          source,
          analysis,
          transcript,
          slides,
          audio_url: audioUrl,
          generated_at: new Date().toISOString(),
        };

        sessionStorage.setItem(
          `meme-workflow-${jobId}`,
          JSON.stringify(resultPayload)
        );

        setProgress(100);
        setStepMessage("Slideshow generated. Opening preview...");
        setStatus("success");

        setTimeout(() => {
          if (!cancelled) {
            navigate(`/result/${jobId}`);
          }
        }, 500);
      } catch (error) {
        if (cancelled) {
          return;
        }

        console.log(error);
        setStatus("error");
        setErrorMessage(
          error.response?.data?.detail || error.message || "Workflow failed."
        );
      }
    };

    runWorkflow();

    return () => {
      cancelled = true;
    };
  }, [audioFile, jobId, navigate, source]);

  return (
    <div
      className="
        min-h-screen
        flex
        items-center
        justify-center
        px-6
        py-12
      "
    >
      <div
        className="
          w-full
          max-w-2xl
          p-8
          shadow-lg
          rounded-xl
          border
        "
      >
        <h1 className="text-3xl font-bold text-center">
          Generating Meme Slideshow 🎬
        </h1>

        <p className="mt-4 text-gray-600 text-center">
          Job ID: <span className="text-sm">{jobId}</span>
        </p>

        <div className="mt-6">
          <progress value={progress} max="100" className="w-full" />
          <p className="mt-3 text-center">{progress}% Complete</p>
          <p className="mt-2 text-center text-sm text-gray-600">{stepMessage}</p>
        </div>

        <div className="mt-8 text-left">
          <h2 className="font-semibold mb-3">Workflow</h2>
          {expectedFlow.map((line) => (
            <p key={line} className="text-sm text-gray-700">
              • {line}
            </p>
          ))}
        </div>

        {status === "error" && (
          <div className="mt-6 p-4 rounded-lg bg-red-50 text-red-700">
            {errorMessage}
          </div>
        )}
      </div>
    </div>
  );
}

export default Processing;
