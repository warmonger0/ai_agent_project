import React, { useEffect, useState } from "react";
import { toast } from "sonner";

import {
  fetchPlugins,
  fetchPluginSpec,
  runPlugin,
} from "@/lib/services/pluginService";

// ✅ PluginSpec imported from pluginService (re-exported)
import { PluginSpec } from "@/lib/services/pluginService";

import { Card, CardContent } from "@/components/ui/card";
import PluginExecutionForm from "@/components/plugin/PluginExecutionForm";
import PluginResult from "@/components/plugin/PluginResult";

export default function PluginPanel() {
  const [plugins, setPlugins] = useState<PluginSpec[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [inputSpec, setInputSpec] = useState<any[]>([]);
  const [inputs, setInputs] = useState<Record<string, string>>({});
  const [result, setResult] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "running" | "success" | "error">("idle");

  useEffect(() => {
    const loadPlugins = async () => {
      try {
        const data = await fetchPlugins();
        setPlugins(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Failed to fetch plugins:", err);
        toast.error("Failed to load plugins.");
        setPlugins([]);
      }
    };
    loadPlugins();
  }, []);

  useEffect(() => {
    const loadSpec = async () => {
      if (!selected) return;
      try {
        const spec = await fetchPluginSpec(selected);
        setInputSpec(Array.isArray(spec) ? spec : []); // ✅ FIXED
      } catch (err) {
        console.error("Failed to fetch plugin spec:", err);
        setInputSpec([]);
        toast.error("Failed to load plugin spec.");
      }
    };
    loadSpec();
  }, [selected]);

  const handleSelectPlugin = (pluginName: string) => {
    setSelected(pluginName);
    setResult(null);
    setInputs({});
    setStatus("idle");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleChange = (name: string, value: string) => {
    setInputs((prev) => ({ ...prev, [name]: value }));
  };

  const handleExecute = async () => {
    if (!selected) return;
    setStatus("running");
    setResult(null);
    try {
      const res = await runPlugin(selected, inputs);
      const formatted =
        typeof res === "object" ? JSON.stringify(res, null, 2) : String(res);
      setResult(formatted);
      setStatus("success");
      toast.success(`✅ "${selected}" plugin executed!`);
      window.dispatchEvent(new Event("plugin-executed"));
    } catch (err) {
      console.error("Plugin execution failed:", err);
      toast.error("❌ Failed to execute plugin.");
      setStatus("error");
    }
  };

  return (
    <Card className="p-6 space-y-8 bg-white rounded-lg shadow-sm">
      <CardContent className="space-y-8">
        <h2 className="text-2xl font-bold text-center">🧩 Plugin Panel</h2>

        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {plugins.map((plugin) => (
            <Card
              key={plugin.module || plugin.name}
              onClick={() => handleSelectPlugin(plugin.module || plugin.name)}
              className={`cursor-pointer transition p-4 text-center ${
                selected === (plugin.module || plugin.name)
                  ? "ring-2 ring-blue-500"
                  : ""
              }`}
            >
              <p className="font-semibold">{plugin.name}</p>
              <p className="text-xs text-gray-500">{plugin.description}</p>
            </Card>
          ))}
        </div>

        {selected && (
          <div className="space-y-6">
            <PluginExecutionForm inputSpec={inputSpec} onChange={handleChange} />

            <div className="flex justify-center">
              <button
                onClick={handleExecute}
                disabled={status === "running"}
                className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded disabled:opacity-50"
              >
                {status === "running" ? "Running..." : "Run Plugin"}
              </button>
            </div>

            {status === "success" && result && <PluginResult result={result} />}

            {status === "error" && (
              <p className="text-center text-red-600 font-semibold">
                ❌ Plugin execution failed.
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
