import { useSearchParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getAnalysis } from "../Services/api";


function formatDuration(seconds) {

  const minutes = Math.floor(seconds / 60);
  const remaining = Math.round(seconds % 60);

  return `${minutes}:${remaining.toString().padStart(2, "0")}`;

}


function Processing() {

  const [searchParams] = useSearchParams();

  const jobId = searchParams.get("job");

  const [progress, setProgress] = useState(10);
  const [status, setStatus] = useState("loading"); // loading | success | error
  const [analysis, setAnalysis] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");


  useEffect(() => {

    const interval = setInterval(() => {

      setProgress((prev)=>{

        if(prev >= 90){
          clearInterval(interval);
          return prev;
        }

        return prev + 10;

      });

    },400);


    return ()=>clearInterval(interval);


  },[]);


  useEffect(() => {

    if(!jobId){
      setStatus("error");
      setErrorMessage("Missing job ID.");
      return;
    }

    let cancelled = false;

    const runAnalysis = async () => {

      try {

        const response = await getAnalysis(jobId);

        if(cancelled) return;

        setAnalysis(response.data);
        setProgress(100);
        setStatus("success");

      } catch(error){

        if(cancelled) return;

        console.log(error);

        setErrorMessage(
          error.response?.data?.detail || "Failed to analyze the audio file."
        );
        setStatus("error");

      }

    };

    runAnalysis();

    return () => { cancelled = true; };

  },[jobId]);


  return (

    <div className="
      min-h-screen
      flex
      items-center
      justify-center
      px-6
      py-12
    ">

      <div className="
        w-full
        max-w-lg
        p-8
        shadow-lg
        rounded-xl
        border
        text-center
      ">


        <h1 className="text-3xl font-bold">
          Analyzing Your Music 🎧
        </h1>


        <p className="mt-4 text-gray-600">
          Job ID:
          <br/>
          <span className="text-sm">
            {jobId}
          </span>
        </p>



        <div className="mt-8">

          <progress
            value={progress}
            max="100"
            className="w-full"
          />

          <p className="mt-3">
            {progress}% Complete
          </p>

        </div>



        <div className="mt-8 text-left">

          <p>✅ Upload completed</p>

          <p>
            {status === "success"
              ? "✅ Analyzing music"
              : status === "error"
                ? "❌ Analyzing music"
                : "⏳ Analyzing music"
            }
          </p>

        </div>


        {
          status === "error" && (

            <div className="mt-6 p-4 rounded-lg bg-red-50 text-red-600 text-left">
              {errorMessage}
            </div>

          )
        }


        {
          status === "success" && analysis && (

            <div className="mt-8 text-left">

              <h2 className="text-xl font-semibold mb-4">
                Analysis Results
              </h2>

              <div className="grid grid-cols-2 gap-4">

                <div className="p-4 rounded-lg border">
                  <p className="text-sm text-gray-500">Duration</p>
                  <p className="text-lg font-bold">
                    {formatDuration(analysis.duration)}
                  </p>
                </div>

                <div className="p-4 rounded-lg border">
                  <p className="text-sm text-gray-500">Tempo</p>
                  <p className="text-lg font-bold">
                    {analysis.bpm} BPM
                  </p>
                </div>

                <div className="p-4 rounded-lg border">
                  <p className="text-sm text-gray-500">Total Beats</p>
                  <p className="text-lg font-bold">
                    {analysis.total_beats}
                  </p>
                </div>

                <div className="p-4 rounded-lg border">
                  <p className="text-sm text-gray-500">Sample Rate</p>
                  <p className="text-lg font-bold">
                    {analysis.sample_rate} Hz
                  </p>
                </div>

              </div>

              <div className="mt-4 p-4 rounded-lg border">

                <p className="text-sm text-gray-500">Average Energy</p>

                <div className="mt-2 w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-black h-3 rounded-full"
                    style={{
                      width: `${Math.min(analysis.average_energy * 100, 100)}%`
                    }}
                  />
                </div>

                <p className="mt-1 text-sm text-gray-600">
                  {analysis.average_energy}
                </p>

              </div>

            </div>

          )
        }


      </div>

    </div>

  );
}


export default Processing;
