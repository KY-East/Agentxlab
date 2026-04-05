import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Search,
  Lightbulb,
  Sparkles,
  ExternalLink,
  MessageSquare,
  X,
  Zap,
  BookOpen,
} from "lucide-react";
import type { DiscoveryResult, RecommendedCombo } from "../../types";

interface Props {
  result: DiscoveryResult;
  onClose: () => void;
  onSelectCombo: (disciplineIds: number[]) => void;
  onGenerateHypothesis: (disciplineIds: number[]) => void;
}

export default function DiscoveryPanel({
  result,
  onClose,
  onSelectCombo,
  onGenerateHypothesis,
}: Props) {
  const navigate = useNavigate();

  const handleDebate = (combo: RecommendedCombo) => {
    const params = new URLSearchParams();
    params.set("disciplines", combo.discipline_ids.join(","));
    if (combo.existing_intersection_id) {
      params.set("intersection", String(combo.existing_intersection_id));
    }
    navigate(`/debate?${params.toString()}`, {
      state: {
        intersectionTitle: combo.intersection_title,
        explanation: combo.explanation_zh || combo.explanation_en,
        direction: combo.direction_zh || combo.direction_en,
        discoveryQuestion: result.question,
        isGap: combo.is_gap,
      },
    });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-3 border-b border-white/10 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2 min-w-0">
          <Search size={14} className="text-violet-400 shrink-0" />
          <h2 className="text-sm font-medium text-white truncate">发现结果</h2>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-white/5 text-gray-500 hover:text-white transition-colors"
        >
          <X size={14} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-5">
        {/* Question */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-3 bg-violet-500/10 border border-violet-500/20 rounded-xl"
        >
          <p className="text-xs text-violet-300 mb-1 flex items-center gap-1">
            <Lightbulb size={12} />
            研究问题
          </p>
          <p className="text-sm text-white leading-relaxed">{result.question}</p>
        </motion.div>

        {/* Matched disciplines */}
        {result.matched_disciplines.length > 0 && (
          <motion.section
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <h3 className="text-xs text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1">
              <BookOpen size={12} />
              相关学科
            </h3>
            <div className="space-y-1.5">
              {result.matched_disciplines.map((m) => (
                <div
                  key={m.discipline_id}
                  className="flex items-start gap-2 p-2 bg-white/[0.02] rounded-lg"
                >
                  <div className="shrink-0 mt-0.5">
                    <div
                      className="w-2 h-2 rounded-full"
                      style={{ opacity: m.relevance }}
                      // Color intensity reflects relevance
                    >
                      <div
                        className="w-full h-full rounded-full bg-violet-400"
                        style={{ opacity: 0.3 + m.relevance * 0.7 }}
                      />
                    </div>
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-white font-medium truncate">
                        {m.name_en}
                      </span>
                      {m.name_zh && (
                        <span className="text-[10px] text-gray-500">{m.name_zh}</span>
                      )}
                      <span className="text-[10px] text-violet-400 ml-auto shrink-0">
                        {Math.round(m.relevance * 100)}%
                      </span>
                    </div>
                    <p className="text-[11px] text-gray-400 mt-0.5 leading-relaxed">
                      {m.reason_zh || m.reason_en}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </motion.section>
        )}

        {/* Recommended combos */}
        {result.recommended_combos.length > 0 && (
          <motion.section
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h3 className="text-xs text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1">
              <Sparkles size={12} />
              推荐研究组合
            </h3>
            <div className="space-y-3">
              {result.recommended_combos.map((combo, i) => (
                <ComboCard
                  key={i}
                  combo={combo}
                  index={i}
                  onSelect={() => onSelectCombo(combo.discipline_ids)}
                  onDebate={() => handleDebate(combo)}
                  onHypothesis={() => onGenerateHypothesis(combo.discipline_ids)}
                />
              ))}
            </div>
          </motion.section>
        )}

        {/* Empty state */}
        {result.matched_disciplines.length === 0 &&
          result.recommended_combos.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500 text-sm">
                未找到匹配的学科，试试换个问法？
              </p>
            </div>
          )}
      </div>
    </div>
  );
}

function ComboCard({
  combo,
  index,
  onSelect,
  onDebate,
  onHypothesis,
}: {
  combo: RecommendedCombo;
  index: number;
  onSelect: () => void;
  onDebate: () => void;
  onHypothesis: () => void;
}) {
  const borderColors = [
    "border-violet-500/30",
    "border-blue-500/30",
    "border-emerald-500/30",
  ];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.1 * index }}
      className={`p-3 bg-white/[0.02] border ${borderColors[index % borderColors.length]} rounded-xl space-y-2`}
    >
      {/* Discipline tags */}
      <div className="flex flex-wrap gap-1">
        {combo.disciplines.map((d) => (
          <span
            key={d.id}
            className="text-[10px] px-2 py-0.5 bg-white/5 text-gray-300 rounded"
          >
            {d.name_zh || d.name_en}
          </span>
        ))}
      </div>

      {/* Explanation */}
      <p className="text-xs text-gray-300 leading-relaxed">
        {combo.explanation_zh || combo.explanation_en}
      </p>

      {/* Direction */}
      <div className="flex items-start gap-1.5 p-2 bg-white/[0.03] rounded-lg">
        <Zap size={11} className="text-amber-400 mt-0.5 shrink-0" />
        <p className="text-[11px] text-gray-400 leading-relaxed">
          {combo.direction_zh || combo.direction_en}
        </p>
      </div>

      {/* Gap / existing status */}
      <div className="flex items-center gap-2">
        {combo.is_gap ? (
          <span className="text-[10px] px-2 py-0.5 bg-red-500/20 text-red-400 rounded">
            研究空白
          </span>
        ) : (
          <span className="text-[10px] px-2 py-0.5 bg-green-500/20 text-green-400 rounded">
            已有研究
          </span>
        )}
        {combo.intersection_title && (
          <span className="text-[10px] text-gray-500 truncate">
            {combo.intersection_title}
          </span>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 pt-1">
        <button
          onClick={onSelect}
          className="flex items-center gap-1 px-2 py-1 text-[10px] bg-violet-600/20 text-violet-300 rounded-lg hover:bg-violet-600/30 transition-colors"
        >
          <ExternalLink size={10} />
          在图谱中查看
        </button>
        {combo.is_gap && (
          <button
            onClick={onHypothesis}
            className="flex items-center gap-1 px-2 py-1 text-[10px] bg-amber-600/20 text-amber-300 rounded-lg hover:bg-amber-600/30 transition-colors"
          >
            <Sparkles size={10} />
            生成假设
          </button>
        )}
        <button
          onClick={onDebate}
          className="flex items-center gap-1 px-2 py-1 text-[10px] bg-blue-600/20 text-blue-300 rounded-lg hover:bg-blue-600/30 transition-colors"
        >
          <MessageSquare size={10} />
          发起辩论
        </button>
      </div>
    </motion.div>
  );
}
