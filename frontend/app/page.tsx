"use client";

import { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import toast from "react-hot-toast";

import {
  Brain,
  Flame,
  MessageSquare,
  FileText,
  SplitSquareVertical,
} from "lucide-react";


const API_URL = process.env.NEXT_PUBLIC_API_URL;
function isValidYoutubeUrl(url: string) {

  try {

    const parsed = new URL(url);

    let videoId = "";

    // youtube.com/watch?v=
    if (
      parsed.hostname.includes("youtube.com")
    ) {

      videoId = parsed.searchParams.get("v") || "";
    }

    // youtu.be/
    else if (
      parsed.hostname.includes("youtu.be")
    ) {

      videoId = parsed.pathname.slice(1);
    }

    // invalid host
    else {

      return false;
    }

    // YouTube IDs are exactly 11 chars
    return /^[a-zA-Z0-9_-]{11}$/.test(videoId);

  } catch {

    return false;
  }
}

export default function HomePage() {

  const [activeTab, setActiveTab] = useState<string>("score");

  const [url, setUrl] = useState("");

  const [video1, setVideo1] = useState("");
  const [video2, setVideo2] = useState("");

  const [question, setQuestion] = useState("");

  const [loading, setLoading] = useState(false);

  const [scoreData, setScoreData] = useState<any>(null);

  const [hookData, setHookData] = useState<any>(null);

  const [chatData, setChatData] = useState<any>(null);

  const [compareData, setCompareData] = useState<any>(null);

  const [transcriptData, setTranscriptData] = useState<any>(null);


  async function analyzeVideo() {

    try {

      setLoading(true);

      const response = await axios.get(
        `${API_URL}/video-score`,
        {
          params: { url }
        }
      );

      setScoreData(response.data);

      toast.success("Video analyzed successfully");

    } catch (error) {

      console.error(error);

      toast.error("Failed to analyze video");

    } finally {

      setLoading(false);
    }
  }


  async function analyzeHook() {

    try {

      setLoading(true);

      const response = await axios.get(
        `${API_URL}/hook-analysis`,
        {
          params: { url }
        }
      );

      setHookData(response.data);

      toast.success("Hook analysis complete");

    } catch (error) {

      console.error(error);

      toast.error("Hook analysis failed");

    } finally {

      setLoading(false);
    }
  }


  async function askQuestion() {

    try {

      setLoading(true);

      const response = await axios.get(
        `${API_URL}/ask`,
        {
          params: {
            query: question,
          },
        }
      );

      setChatData(response.data);

      toast.success("AI answer generated");

    } catch (error) {

      console.error(error);

      toast.error("Chat request failed");

    } finally {

      setLoading(false);
    }
  }


  async function compareVideos() {

    try {

      setLoading(true);

      const response = await axios.get(
        `${API_URL}/compare`,
        {
          params: {
            video1,
            video2,
            query: question,
          },
        }
      );

      setCompareData(response.data);

      toast.success("Comparison complete");

    } catch (error) {

      console.error(error);

      toast.error("Comparison failed");

    } finally {

      setLoading(false);
    }
  }


  async function getTranscript() {

    try {

      setLoading(true);

      const response = await axios.get(
        `${API_URL}/transcript`,
        {
          params: { url }
        }
      );

      setTranscriptData(response.data);

      toast.success("Transcript loaded");

    } catch (error) {

      console.error(error);

      toast.error("Transcript fetch failed");

    } finally {

      setLoading(false);
    }
  }


  const analysis = scoreData?.analysis;


  return (

    <main className="min-h-screen bg-black text-white flex">

      {/* SIDEBAR */}
      <aside className="w-72 border-r border-zinc-800 bg-zinc-950 p-6">

        <h1 className="text-3xl font-bold mb-10 bg-gradient-to-r from-purple-400 to-pink-500 text-transparent bg-clip-text">
          Creator AI
        </h1>

        <div className="space-y-3">

          <SidebarButton
            icon={<Brain size={18} />}
            label="Video Score"
            active={activeTab === "score"}
            onClick={() => setActiveTab("score")}
          />

          <SidebarButton
            icon={<Flame size={18} />}
            label="Hook Analysis"
            active={activeTab === "hook"}
            onClick={() => setActiveTab("hook")}
          />

          <SidebarButton
            icon={<MessageSquare size={18} />}
            label="AI Creator Chat"
            active={activeTab === "chat"}
            onClick={() => setActiveTab("chat")}
          />

          <SidebarButton
            icon={<SplitSquareVertical size={18} />}
            label="Compare Videos"
            active={activeTab === "compare"}
            onClick={() => setActiveTab("compare")}
          />

          <SidebarButton
            icon={<FileText size={18} />}
            label="Transcript"
            active={activeTab === "transcript"}
            onClick={() => setActiveTab("transcript")}
          />
        </div>
      </aside>


      {/* MAIN */}
      <section className="flex-1 p-10 overflow-y-auto">

        <div className="max-w-6xl mx-auto">

          <h2 className="text-5xl font-bold mb-3">
            Creator Intelligence Platform
          </h2>

          <p className="text-zinc-400 mb-10 text-lg">
            AI-powered creator analysis for storytelling, hooks, retention, and virality.
          </p>


          {/* INPUT */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-3xl p-6 mb-10">

            <div className="flex gap-4">

              <input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Paste YouTube video URL"
                className="flex-1 bg-zinc-950 border border-zinc-700 rounded-2xl px-5 py-4 outline-none"
              />

              <button

                disabled={loading}

                onClick={() => {

  // CHAT TAB DOES NOT NEED URL
  if (activeTab !== "chat") {

    // COMPARE TAB VALIDATION
    if (activeTab === "compare") {

      if (
        !isValidYoutubeUrl(video1) ||
        !isValidYoutubeUrl(video2)
      ) {

        toast.error("Please enter valid YouTube URLs");

        return;
      }

    } else {

      // NORMAL TABS VALIDATION
      if (!isValidYoutubeUrl(url)) {

        toast.error("Please enter a valid YouTube URL");

        return;
      }
    }
  }

  // RUN ACTIONS
  if (activeTab === "score") {

    analyzeVideo();

  } else if (activeTab === "hook") {

    analyzeHook();

  } else if (activeTab === "chat") {

    askQuestion();

  } else if (activeTab === "compare") {

    compareVideos();

  } else if (activeTab === "transcript") {

    getTranscript();
  }
}}

                className="bg-gradient-to-r from-purple-500 to-pink-500 px-8 py-4 rounded-2xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >

                {loading ? (

                  <div className="flex items-center gap-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Running...
                  </div>

                ) : (

                  "Run AI"
                )}
              </button>
            </div>
          </div>


          {/* SCORE */}
          {activeTab === "score" && analysis && (

            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">

                <ScoreCard title="Hook Score" score={analysis.hook_score} />

                <ScoreCard title="Emotion Score" score={analysis.emotion_score} />

                <ScoreCard title="Retention Score" score={analysis.retention_score} />

                <ScoreCard title="Virality Score" score={analysis.virality_score} />

                <ScoreCard title="Storytelling" score={analysis.storytelling_score} />

                <ScoreCard title="Overall" score={analysis.overall_score} />
              </div>


              <div className="grid lg:grid-cols-3 gap-6">

                <AnalysisCard
                  title="Strengths"
                  items={analysis.strengths}
                />

                <AnalysisCard
                  title="Weaknesses"
                  items={analysis.weaknesses}
                />

                <AnalysisCard
                  title="Improvements"
                  items={analysis.improvements}
                />
              </div>
            </>
          )}


          {/* HOOK */}
          {activeTab === "hook" && hookData && (

            <div className="bg-zinc-900 border border-zinc-800 rounded-3xl p-8 text-zinc-300 leading-8 prose prose-invert max-w-none">

              <ReactMarkdown>
                {hookData.analysis}
              </ReactMarkdown>

            </div>
          )}


          {/* CHAT */}
          {activeTab === "chat" && (

            <div className="space-y-6">

              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask creator intelligence question"
                className="w-full bg-zinc-900 border border-zinc-700 rounded-2xl px-5 py-4 outline-none"
              />

              {chatData && (

                <>
                  <div className="bg-zinc-900 border border-zinc-800 rounded-3xl p-8 text-zinc-300 leading-8 prose prose-invert max-w-none">

                    <ReactMarkdown>
                      {chatData.answer}
                    </ReactMarkdown>

                  </div>


                  <div className="space-y-4">

                    {chatData.citations?.map((item: any, index: number) => (

                      <div
                        key={index}
                        className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5"
                      >

                        <div className="text-purple-400 font-semibold mb-2">
                          {item.citation}
                        </div>

                        <div className="text-zinc-300">
                          {item.text}
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}


          {/* COMPARE */}
          {activeTab === "compare" && (

            <div className="space-y-6">

              <input
                value={video1}
                onChange={(e) => setVideo1(e.target.value)}
                placeholder="Video 1 URL"
                className="w-full bg-zinc-900 border border-zinc-700 rounded-2xl px-5 py-4"
              />

              <input
                value={video2}
                onChange={(e) => setVideo2(e.target.value)}
                placeholder="Video 2 URL"
                className="w-full bg-zinc-900 border border-zinc-700 rounded-2xl px-5 py-4"
              />

              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Comparison question"
                className="w-full bg-zinc-900 border border-zinc-700 rounded-2xl px-5 py-4"
              />

              {compareData && (

                <div className="bg-zinc-900 border border-zinc-800 rounded-3xl p-8 text-zinc-300 leading-8 prose prose-invert max-w-none">

                  <ReactMarkdown>
                    {compareData.comparison}
                  </ReactMarkdown>

                </div>
              )}
            </div>
          )}


          {/* TRANSCRIPT */}
          {activeTab === "transcript" && transcriptData && (

            <div className="bg-zinc-900 border border-zinc-800 rounded-3xl p-8">

              <div className="space-y-5 max-h-[700px] overflow-y-auto">

                {transcriptData.segments?.map((segment: any, index: number) => (

                  <div
                    key={index}
                    className="border-b border-zinc-800 pb-4"
                  >

                    <div className="text-purple-400 text-sm mb-2">
                      {segment.start.toFixed(2)}s
                    </div>

                    <div className="text-zinc-300 leading-7">
                      {segment.text}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}


function SidebarButton({
  icon,
  label,
  active,
  onClick,
}: any) {

  return (

    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-5 py-4 rounded-2xl transition ${
        active
          ? "bg-gradient-to-r from-purple-500 to-pink-500"
          : "bg-zinc-900 hover:bg-zinc-800"
      }`}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}


function ScoreCard({ title, score }: any) {

  return (

    <div className="bg-zinc-900 border border-zinc-800 rounded-3xl p-6">

      <div className="text-zinc-400 mb-3">
        {title}
      </div>

      <div className="text-5xl font-bold">
        {score}
      </div>
    </div>
  );
}


function AnalysisCard({ title, items }: any) {

  return (

    <div className="bg-zinc-900 border border-zinc-800 rounded-3xl p-6">

      <h3 className="text-2xl font-bold mb-5">
        {title}
      </h3>

      <div className="space-y-4">

        {items?.map((item: string, index: number) => (

          <div
            key={index}
            className="bg-zinc-950 border border-zinc-800 rounded-2xl p-4 text-zinc-300"
          >
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}