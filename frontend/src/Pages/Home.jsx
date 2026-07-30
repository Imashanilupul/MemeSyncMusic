import { Link } from "react-router-dom";

function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6">

      <h1 className="text-5xl font-bold text-center">
        MemeSync AI 🎵😂
      </h1>

      <p className="mt-5 text-lg text-gray-600 text-center max-w-xl">
        Turn your favorite songs into AI-generated meme slideshow videos.
        Upload your music and let AI match memes with your lyrics and mood.
      </p>


      <Link
        to="/upload"
        className="mt-8 px-8 py-3 rounded-lg bg-black text-white 
                   hover:bg-gray-800 transition"
      >
        Create Meme Video
      </Link>


      <div className="grid md:grid-cols-3 gap-6 mt-16">

        <FeatureCard
          title="🎵 Music Analysis"
          description="AI analyzes beats, lyrics, and emotions from your song."
        />


        <FeatureCard
          title="😂 Meme Matching"
          description="Finds suitable memes based on song meaning."
        />


        <FeatureCard
          title="🎬 Video Generation"
          description="Creates a synced meme slideshow video."
        />

      </div>

    </div>
  );
}


function FeatureCard({title, description}) {

  return (
    <div className="
      p-6 rounded-xl shadow-md 
      border bg-white
      w-64
    ">

      <h3 className="font-bold text-xl">
        {title}
      </h3>

      <p className="mt-3 text-gray-600">
        {description}
      </p>

    </div>
  );
}


export default Home;