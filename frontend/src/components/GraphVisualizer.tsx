import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { api } from "../services/api";
import { Info, HelpCircle, GitCommit, FileText, Database, ShieldAlert, Award, User } from "lucide-react";

// Node & Link structures representing backend JSON payload
interface GraphNode extends d3.SimulationNodeDatum {
  id: string;
  label: string;
  type: string;
  properties?: Record<string, any>;
}

interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
  source: string | GraphNode;
  target: string | GraphNode;
  type: string;
}

export const GraphVisualizer: React.FC = () => {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>({ nodes: [], links: [] });

  useEffect(() => {
    fetchGraph();
  }, []);

  const fetchGraph = async () => {
    setLoading(true);
    try {
      const data = await api.getGraphData();
      setGraphData(data);
      setError("");
    } catch (err: any) {
      setError(err.message || "Failed to load knowledge graph data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!svgRef.current || graphData.nodes.length === 0) return;

    // Reset previous drawing
    d3.select(svgRef.current).selectAll("*").remove();

    const width = containerRef.current?.clientWidth || 800;
    const height = 550;

    const svg = d3.select(svgRef.current)
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [0, 0, width, height]);

    // Graph Colors by entity category
    const colors: Record<string, string> = {
      Paper: "#6366f1",      // Indigo
      Author: "#64748b",     // Slate
      Topic: "#8b5cf6",      // Violet
      Dataset: "#06b6d4",    // Cyan
      Algorithm: "#10b981",  // Emerald
      ResearchGap: "#f59e0b" // Amber
    };

    // Zoom and pan container setup
    const g = svg.append("g");

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    svg.call(zoom);

    // Deep copy arrays for D3 mutation
    const nodes: GraphNode[] = graphData.nodes.map(d => ({ ...d }));
    const links: GraphLink[] = graphData.links.map(d => ({ ...d }));

    // Simulation forces
    const simulation = d3.forceSimulation<GraphNode>(nodes)
      .force("link", d3.forceLink<GraphNode, GraphLink>(links)
        .id(d => d.id)
        .distance(110)
      )
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(35));

    // Draw Links
    const link = g.append("g")
      .attr("stroke", "#94a3b8")
      .attr("stroke-opacity", 0.5)
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke-width", 2.5);

    // Draw Nodes group
    const node = g.append("g")
      .selectAll("g")
      .data(nodes)
      .join("g")
      .attr("class", "node-group")
      .style("cursor", "pointer")
      .on("click", (_event, d) => {
        setSelectedNode(d);
      })
      .call(
        d3.drag<any, any>()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended) as any
      );

    // Node circles (colored based on entity type)
    node.append("circle")
      .attr("r", 20)
      .attr("fill", d => colors[d.type] || "#475569")
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 2.5)
      .attr("class", "transition-all duration-300 hover:scale-115 shadow-md");

    // Text labels beside/below nodes
    node.append("text")
      .text(d => d.label)
      .attr("x", 0)
      .attr("y", 32)
      .attr("text-anchor", "middle")
      .attr("font-size", "11px")
      .attr("font-weight", "500")
      .attr("fill", "currentColor")
      .attr("class", "bg-transparent font-sans drop-shadow-sm select-none opacity-80 pointer-events-none");

    // Node icon letters
    node.append("text")
      .text(d => d.type[0])
      .attr("x", 0)
      .attr("y", 5)
      .attr("text-anchor", "middle")
      .attr("fill", "#ffffff")
      .attr("font-size", "13px")
      .attr("font-weight", "bold")
      .attr("class", "pointer-events-none select-none");

    // Animation frames update positions
    simulation.on("tick", () => {
      link
        .attr("x1", d => (d.source as GraphNode).x || 0)
        .attr("y1", d => (d.source as GraphNode).y || 0)
        .attr("x2", d => (d.target as GraphNode).x || 0)
        .attr("y2", d => (d.target as GraphNode).y || 0);

      node
        .attr("transform", d => `translate(${d.x || 0}, ${d.y || 0})`);
    });

    // Drag helpers
    function dragstarted(event: any, d: GraphNode) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: GraphNode) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: GraphNode) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    return () => {
      simulation.stop();
    };
  }, [graphData]);

  // Sidebar details helper functions
  const getNodeIcon = (type: string) => {
    switch (type) {
      case "Paper": return <FileText className="w-5 h-5 text-indigo-500" />;
      case "Author": return <User className="w-5 h-5 text-slate-500" />;
      case "Topic": return <GitCommit className="w-5 h-5 text-violet-500" />;
      case "Dataset": return <Database className="w-5 h-5 text-cyan-500" />;
      case "Algorithm": return <Award className="w-5 h-5 text-emerald-500" />;
      case "ResearchGap": return <ShieldAlert className="w-5 h-5 text-amber-500" />;
      default: return <HelpCircle className="w-5 h-5 text-slate-400" />;
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6" ref={containerRef}>
      {/* Graph Visualizer Panel */}
      <div className="lg:col-span-3 glass-panel rounded-2xl relative overflow-hidden flex flex-col h-[550px]">
        {/* Legends */}
        <div className="absolute top-4 left-4 z-10 flex flex-wrap gap-3 text-xs bg-white/80 dark:bg-[#0f172a]/80 backdrop-blur px-3 py-2 rounded-xl border border-slate-200/50 dark:border-slate-800/50 shadow">
          <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-indigo-500"></span>Paper</div>
          <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-slate-500"></span>Author</div>
          <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-violet-500"></span>Topic</div>
          <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-cyan-500"></span>Dataset</div>
          <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>Algorithm</div>
          <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>Research Gap</div>
        </div>

        {/* Refresh button */}
        <button
          onClick={fetchGraph}
          className="absolute top-4 right-4 z-10 px-3 py-1 bg-accent-primary text-white hover:bg-accent-dark text-xs font-semibold rounded-lg shadow-md transition-all duration-300"
        >
          Reset Graph View
        </button>

        {loading ? (
          <div className="flex-1 flex flex-col items-center justify-center space-y-3">
            <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-sm opacity-60">Rendering Knowledge Graph...</p>
          </div>
        ) : error ? (
          <div className="flex-1 flex items-center justify-center p-6 text-red-500 text-sm">
            {error}
          </div>
        ) : (
          <svg ref={svgRef} className="flex-1 w-full text-slate-700 dark:text-slate-300" />
        )}
      </div>

      {/* Selected Node Details side panel */}
      <div className="glass-panel rounded-2xl p-6 flex flex-col justify-between h-[550px]">
        <div>
          <h3 className="text-lg font-bold border-b border-slate-200/50 dark:border-slate-800/50 pb-3 flex items-center gap-2">
            <Info className="w-5 h-5 text-indigo-500" />
            Entity Inspector
          </h3>

          {selectedNode ? (
            <div className="mt-5 space-y-4 overflow-y-auto max-h-[350px] pr-1">
              <div className="flex items-center gap-3">
                {getNodeIcon(selectedNode.type)}
                <div>
                  <span className="text-[10px] tracking-wider uppercase font-semibold text-slate-400">
                    {selectedNode.type} Node
                  </span>
                  <h4 className="text-md font-bold text-slate-800 dark:text-slate-100 leading-snug">
                    {selectedNode.label}
                  </h4>
                </div>
              </div>

              {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
                <div className="space-y-3 pt-3 border-t border-slate-200/50 dark:border-slate-800/50">
                  {Object.entries(selectedNode.properties).map(([key, val]) => {
                    // Skip uid and clean display
                    if (key === "uid" || key === "id") return null;
                    return (
                      <div key={key} className="space-y-1">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                          {key.replace("_", " ")}
                        </span>
                        <p className="text-xs text-slate-600 dark:text-slate-300 font-medium whitespace-pre-line leading-relaxed">
                          {String(val)}
                        </p>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          ) : (
            <div className="mt-20 text-center space-y-3 opacity-60">
              <HelpCircle className="w-10 h-10 mx-auto text-slate-400" />
              <p className="text-xs">Click a graph node to inspect relationships and attributes.</p>
            </div>
          )}
        </div>

        <div className="text-[10px] text-center opacity-40 pt-4 border-t border-slate-200/50 dark:border-slate-800/50">
          Knowledge Graph visualization compiles dynamic citations across authors, algorithms, and models.
        </div>
      </div>
    </div>
  );
};
