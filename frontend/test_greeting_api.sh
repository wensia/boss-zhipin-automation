#!/bin/bash

echo "=== 测试打招呼API ==="
echo

echo "1. 获取初始状态"
curl -s http://localhost:27421/api/greeting/status | python3 -m json.tool
echo

echo "2. 启动打招呼任务（2个候选人）"
curl -s -X POST http://localhost:27421/api/greeting/start \
  -H "Content-Type: application/json" \
  -d '{"target_count": 2}' | python3 -m json.tool
echo

echo "3. 等待3秒后查看状态"
sleep 3
curl -s http://localhost:27421/api/greeting/status | python3 -m json.tool
echo

echo "4. 查看日志"
curl -s http://localhost:27421/api/greeting/logs?last_n=10 | python3 -m json.tool
