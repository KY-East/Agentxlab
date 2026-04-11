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
const VerifyEmail = lazy(() => import("./pages/VerifyEmail"));
const ResetPassword = lazy(() => import("./pages/ResetPassword"));

const LazyFallback = <div className="p-8 text-gray-400">Loading...</div>;

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
        <Route path="profile" element={<Suspense fallback={LazyFallback}><Profile /></Suspense>} />
        <Route path="verify-email" element={<Suspense fallback={LazyFallback}><VerifyEmail /></Suspense>} />
        <Route path="reset-password" element={<Suspense fallback={LazyFallback}><ResetPassword /></Suspense>} />
      </Route>
    </Routes>
  );
}
