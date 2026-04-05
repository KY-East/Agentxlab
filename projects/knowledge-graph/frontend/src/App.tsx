import { Routes, Route } from "react-router-dom";
import { lazy, Suspense } from "react";
import Layout from "./components/Layout/Layout";
import Home from "./pages/Home";
import Canvas from "./pages/Canvas";
import Debate from "./pages/Debate";
import DebateSession from "./pages/DebateSession";
import Forum from "./pages/Forum";
import PaperEditor from "./pages/PaperEditor";
import ForumPostDetail from "./pages/ForumPostDetail";

const Profile = lazy(() => import("./pages/Profile"));

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="canvas" element={<Canvas />} />
        <Route path="debate" element={<Debate />} />
        <Route path="debate/:debateId" element={<DebateSession />} />
        <Route path="paper/:draftId" element={<PaperEditor />} />
        <Route path="forum" element={<Forum />} />
        <Route path="forum/:postId" element={<ForumPostDetail />} />
        <Route
          path="profile"
          element={
            <Suspense fallback={<div className="p-8 text-gray-400">Loading...</div>}>
              <Profile />
            </Suspense>
          }
        />
      </Route>
    </Routes>
  );
}
