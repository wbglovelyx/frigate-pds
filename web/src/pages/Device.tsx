import Heading from "@/components/ui/heading";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";

export default function DeviceOverview() {
  const [plcLinked, setPlcLinked] = useState(false);

  useEffect(() => {
    document.title = "设备总览";
  }, []);

  const togglePlcLink = () => {
    // TODO: 修改配置文件中PLC连锁状态
    setPlcLinked((prev) => !prev);
  };

  return (
    <div className="flex min-h-screen flex-col bg-gray-50 font-sans text-gray-800">
      {/* 上部分 1.5 */}
      <div className="flex flex-[1.5] items-center justify-center border-b bg-white p-6 shadow">
        <Heading as="h1" className="text-2xl font-bold text-blue-600">
          设备总览
        </Heading>
      </div>

      {/* 中间部分 7 */}
      <div className="flex flex-[7] gap-6 px-6 py-6">
        {/* 左侧：雷达数据 */}
        <div className="w-1/2 space-y-6">
          <div className="rounded-xl bg-white p-4 shadow">
            <h2 className="mb-2 text-lg font-semibold">雷达模块信息</h2>
            <table className="w-full border border-gray-300 text-sm">
              <thead className="bg-blue-100">
                <tr>
                  <th className="border px-2 py-1">树莓派名称</th>
                  <th className="border px-2 py-1">IP地址</th>
                  <th className="border px-2 py-1">雷达模块</th>
                  <th className="border px-2 py-1">存活状态</th>
                  <th className="border px-2 py-1">探测情况</th>
                </tr>
              </thead>
              <tbody>
                <tr className="text-center">
                  <td className="border px-2 py-1">RPI-01</td>
                  <td className="border px-2 py-1">192.168.1.10</td>
                  <td className="border px-2 py-1">Radar-A</td>
                  <td className="border px-2 py-1 text-green-600">在线</td>
                  <td className="border px-2 py-1">有人</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* 准确率图 placeholder */}
          <div className="flex h-56 items-center justify-center rounded-xl bg-white p-4 shadow">
            <span className="text-gray-400">[ 准确率图表 ]</span>
          </div>
        </div>

        {/* 右侧：摄像头数据 */}
        <div className="w-1/2 space-y-6">
          <div className="rounded-xl bg-white p-4 shadow">
            <h2 className="mb-2 text-lg font-semibold">摄像头信息</h2>
            <table className="w-full border border-gray-300 text-sm">
              <thead className="bg-blue-100">
                <tr>
                  <th className="border px-2 py-1">名称</th>
                  <th className="border px-2 py-1">IP地址</th>
                  <th className="border px-2 py-1">在线状态</th>
                  <th className="border px-2 py-1">当前状态</th>
                </tr>
              </thead>
              <tbody>
                <tr className="text-center">
                  <td className="border px-2 py-1">Camera-01</td>
                  <td className="border px-2 py-1">192.168.1.20</td>
                  <td className="border px-2 py-1 text-green-600">在线</td>
                  <td className="border px-2 py-1">有人</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* 显示区 */}
          <div className="h-32 overflow-auto rounded-xl bg-white p-4 shadow">
            <p className="text-sm">目标出现：2025-06-11 10:22</p>
          </div>
        </div>
      </div>

      {/* 下部分 1.5 */}
      <div className="flex flex-[1.5] items-center justify-center space-x-4 border-t bg-white p-6 shadow-inner">
        <span className="text-base">
          PLC 连锁状态：
          <span
            className={plcLinked ? "ml-2 text-green-600" : "ml-2 text-red-500"}
          >
            {plcLinked ? "已连锁" : "未连锁"}
          </span>
        </span>
        <Button
          onClick={togglePlcLink}
          className="ml-4 rounded-full bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          {plcLinked ? "取消连锁" : "连锁PLC"}
        </Button>
      </div>
    </div>
  );
}
