import { useSearchParams } from "react-router-dom";
import { useEffect, useState } from "react";


function Processing() {

  const [searchParams] = useSearchParams();

  const jobId = searchParams.get("job");

  const [progress, setProgress] = useState(10);


  useEffect(() => {

    // Later connect this with backend status API

    const interval = setInterval(() => {

      setProgress((prev)=>{

        if(prev >= 90){
          clearInterval(interval);
          return prev;
        }

        return prev + 10;

      });

    },2000);


    return ()=>clearInterval(interval);


  },[]);



  return (

    <div className="
      min-h-screen
      flex
      items-center
      justify-center
      px-6
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
          Creating Your Meme Video 🎬
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
            {progress >= 30 
              ? "✅ Analyzing music"
              : "⏳ Analyzing music"
            }
          </p>


          <p>
            {progress >= 50
              ? "✅ Finding memes"
              : "⏳ Finding memes"
            }
          </p>


          <p>
            {progress >= 80
              ? "✅ Rendering video"
              : "⏳ Rendering video"
            }
          </p>


        </div>


      </div>

    </div>

  );
}


export default Processing;