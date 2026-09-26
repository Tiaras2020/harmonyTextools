#!/usr/bin/env python3
"""Opt-in TeXstudio application client; no HDC or direct compiler invocation."""
import argparse
import json
import socket
import sys
import time
from pathlib import Path

# BEGIN GENERATED HELP
CLI_HELP = json.loads('{"schema":1,"protocol":1,"appliesTo":"TeXstudio Harmony 1.0.29","usage":"python3 texstudioctl.py --session texstudio-session.json COMMAND [参数]","offlineHelp":["python3 texstudioctl.py help","python3 texstudioctl.py help build","python3 texstudioctl.py help --json"],"notes":["protocol、host、port、token 是连接参数，请勿随意修改；help 是说明，编辑说明不会改变应用支持的命令。","示例中的 main.tex、chapters/intro.tex、TASK_ID 和行号可替换；路径相对已授权工程目录，带空格时加引号。","ok=true 仅表示请求处理成功。编译完成后必须看 terminal、buildSucceeded 和 state；排队或运行中 buildSucceeded/exitCode 为 null。","AI 可以直接修改工程磁盘文件；调用 project.refresh 后检查 modified/conflict。未保存内容或冲突会阻止构建，不会自动保存。","连接文件含令牌，只交给获授权的本地工具；关闭会话后失效。示例故意不含令牌。","完整输出在 job.logs；diagnostics 仅为有限诊断。旧 PDF 存在不代表本次编译成功。","实际可用命令以连接应用的 capabilities 为准。这里的示例是说明，客户端不会自动执行它们。","构建只检查授权工程内已打开缓冲区；unsaved_edits 的 blockers 列出具体路径、modified、conflict、exists。工程外编辑不自动保存，也不阻止此工程构建。","连接成功后会话面板收起到左侧 CLI 入口；后台打开、构建不主动置顶应用。关闭会话仍会撤销授权。","磁盘与缓冲区按当前编码解码、统一换行后内容一致时，刷新可自动解除冲突并标记已保存，保留撤销历史。","document.reload 默认保护未保存修改。明确采用磁盘内容时，先 document.read，再传 --discard-local --expected-revision REV；版本变化会拒绝。成功替换内容会清空旧撤销历史。不要自动丢弃用户编辑。"],"resultFields":{"ok":"请求处理成功，不代表编译成功","terminal":"任务是否结束","buildSucceeded":"成功 true；失败或取消 false；运行中 null","state":"queued/running/succeeded/failed/cancelled","exitCode":"任务结束后的进程退出码；取消还需看 state","job":"任务 ID，用于查询同一任务","blockers":"阻塞构建的授权工程缓冲区，包括磁盘已删除文件"},"clientOptions":{"--session":"连接 JSON 路径；离线 help 不需要","--wait":"build/build.clean 等待所提交任务完成","--timeout":"等待秒数，默认 300；超时不会自动取消构建","--json":"help 输出适合 AI 读取的 JSON"},"workflow":["project.refresh","documents.list","build --path main.tex --engine xelatex --wait","diagnostics --job TASK_ID","artifact.info --job TASK_ID"],"commands":{"help":{"summary":"离线查看全部命令或单条命令；不连接应用","parameters":{"topic":"可选命令名","--json":"输出 JSON"},"example":"python3 texstudioctl.py help build --json"},"capabilities":{"summary":"查询当前应用版本、实际支持的命令和限制","parameters":{},"request":{"command":"capabilities"},"example":"python3 texstudioctl.py --session texstudio-session.json capabilities"},"status":{"summary":"查询最新任务及应用忙碌状态","parameters":{},"request":{"command":"status"},"example":"python3 texstudioctl.py --session texstudio-session.json status"},"project.info":{"summary":"查询授权根目录和主文件","parameters":{},"request":{"command":"project.info"},"example":"python3 texstudioctl.py --session texstudio-session.json project.info"},"project.refresh":{"summary":"检查授权工程中已打开文件的外部变化，返回编辑/冲突状态","parameters":{},"request":{"command":"project.refresh"},"example":"python3 texstudioctl.py --session texstudio-session.json project.refresh"},"files.list":{"summary":"分页列出一个目录，不递归扫描整个工程","parameters":{"--path":"目录相对路径，默认 .","--offset":"从 0 开始，默认 0","--limit":"1–500，默认 100"},"request":{"command":"files.list","path":".","offset":0,"limit":100},"example":"python3 texstudioctl.py --session texstudio-session.json files.list --path . --offset 0 --limit 100"},"documents.list":{"summary":"列出授权工程中已打开文档的 modified、conflict、master 状态","parameters":{},"request":{"command":"documents.list"},"example":"python3 texstudioctl.py --session texstudio-session.json documents.list"},"document.read":{"summary":"读取文本，已打开文件优先读取编辑缓冲区；先检查外部变化","parameters":{"--path":"必填，工程内文本文件","--start":"起始行，从 1 开始，默认 1","--count":"1–2000 行，默认 200"},"limits":"文件至多 4 MiB；响应片段至多 256 KiB；未打开文件按 UTF-8 读取","request":{"command":"document.read","path":"chapters/intro.tex","start":1,"count":100},"example":"python3 texstudioctl.py --session texstudio-session.json document.read --path chapters/intro.tex --start 1 --count 100"},"document.open":{"summary":"在应用中打开工程内 .tex 文件","parameters":{"--path":"必填，.tex 相对路径"},"request":{"command":"document.open","path":"main.tex"},"example":"python3 texstudioctl.py --session texstudio-session.json document.open --path main.tex"},"master.set":{"summary":"设置工程主 .tex 文件","parameters":{"--path":"必填，.tex 相对路径"},"request":{"command":"master.set","path":"main.tex"},"example":"python3 texstudioctl.py --session texstudio-session.json master.set --path main.tex"},"build":{"summary":"提交应用内编译，返回任务 ID；--wait 等待结果","parameters":{"--path":"主 .tex 相对路径，省略使用会话主文件","--engine":"pdflatex/xelatex/lualatex，客户端默认 xelatex","--wait":"等待完成；失败/取消返回非零客户端退出码"},"request":{"command":"build","path":"main.tex","engine":"xelatex"},"example":"python3 texstudioctl.py --session texstudio-session.json build --path main.tex --engine xelatex --wait"},"build.clean":{"summary":"删除主文件的 .fdb_latexmk 失败缓存，并强制重新编译；保留源文件和原 PDF","parameters":{"--path":"主 .tex 相对路径","--engine":"pdflatex/xelatex/lualatex，默认 xelatex","--wait":"等待完成"},"request":{"command":"build.clean","path":"main.tex","engine":"xelatex"},"example":"python3 texstudioctl.py --session texstudio-session.json build.clean --path main.tex --engine xelatex --wait"},"job.status":{"summary":"查询指定任务的状态与明确构建结果","parameters":{"--job":"任务 ID，省略为最新任务"},"request":{"command":"job.status","job":"TASK_ID"},"example":"python3 texstudioctl.py --session texstudio-session.json job.status --job TASK_ID"},"job.logs":{"summary":"增量读取任务日志；用返回的 nextOffset 继续读取","parameters":{"--job":"任务 ID","--offset":"UTF-16 单元偏移，默认 0","--limit":"1–65536，默认 16384"},"request":{"command":"job.logs","job":"TASK_ID","offset":0,"limit":16384},"example":"python3 texstudioctl.py --session texstudio-session.json job.logs --job TASK_ID --offset 0 --limit 16384"},"logs":{"summary":"兼容旧客户端的日志尾部，最多 65536 字符","parameters":{"--job":"任务 ID，省略为最新任务"},"request":{"command":"logs","job":"TASK_ID"},"example":"python3 texstudioctl.py --session texstudio-session.json logs --job TASK_ID"},"diagnostics":{"summary":"读取最终轮有限诊断；缓存失败时返回恢复提示","parameters":{"--job":"任务 ID，省略为最新任务"},"request":{"command":"diagnostics","job":"TASK_ID"},"example":"python3 texstudioctl.py --session texstudio-session.json diagnostics --job TASK_ID"},"artifact.info":{"summary":"查询主文件同目录 PDF 摘要及任务归属；不验证页数或视觉正确性","parameters":{"--job":"任务 ID，省略为最新任务"},"request":{"command":"artifact.info","job":"TASK_ID"},"example":"python3 texstudioctl.py --session texstudio-session.json artifact.info --job TASK_ID"},"cancel":{"summary":"请求取消当前正在运行的任务；随后查询 job.status 确认结束","parameters":{"--job":"任务 ID，省略为最新任务"},"request":{"command":"cancel","job":"TASK_ID"},"example":"python3 texstudioctl.py --session texstudio-session.json cancel --job TASK_ID"},"resources":{"summary":"查询运行资源版本、用户资源启用状态和搜索路径","parameters":{},"request":{"command":"resources"},"example":"python3 texstudioctl.py --session texstudio-session.json resources"},"document.reload":{"summary":"从磁盘重载已打开文本；默认不丢弃未保存编辑","parameters":{"--path":"必填，授权工程内已打开文本文件","--discard-local":"明确丢弃本地编辑，必须配合版本校验","--expected-revision":"document.read 返回的 revision；不匹配则拒绝"},"request":{"command":"document.reload","path":"main.tex"},"example":"python3 texstudioctl.py --session texstudio-session.json document.reload --path main.tex","limits":"4 MiB；按编辑器当前编码读取；忙碌、缺失、无效编码和旧版本均拒绝。强制示例：document.reload --path main.tex --discard-local --expected-revision REV","errors":{"file_missing":"授权工程内路径合法，但磁盘文件已不存在；先恢复磁盘文件。","invalid_text_path":"路径不合法、越界、隐藏路径、符号链接或不支持的文件类型。","document_not_open":"文件存在，但未在应用内打开。","read_failed":"文件存在，但无法读取。"}}}}')
# END GENERATED HELP

def request(session, command, engine=None, **parameters):
    if session.get('protocol') != 1 or session.get('host') != '127.0.0.1':
        raise ValueError('Unsupported session descriptor')
    port = session.get('port')
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError('Invalid session port')
    message = dict(parameters)
    message.update(token=session['token'], command=command)
    if engine:
        message['engine'] = engine
    with socket.create_connection(('127.0.0.1', port), timeout=5) as sock:
        sock.sendall(json.dumps(message).encode('utf-8') + b'\n')
        with sock.makefile('rb') as response:
            data = response.readline(1024 * 1024)
    if not data.endswith(b'\n'):
        raise ValueError('Incomplete or oversized application response')
    return json.loads(data)

def main():
    parser = argparse.ArgumentParser(description='TeXstudio 鸿蒙应用 CLI；help 无需连接文件或运行应用。',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='命令：\n'+'\n'.join('  '+name+' — '+item['summary'] for name,item in CLI_HELP['commands'].items())+'\n\n示例：python3 texstudioctl.py help build\nAI 使用：python3 texstudioctl.py help --json')
    parser.add_argument('--session', type=Path, help='连接 JSON；执行应用命令时必填')
    parser.add_argument('command', nargs='?', default='help', choices=list(CLI_HELP['commands']))
    parser.add_argument('topic', nargs='?', help='help 的可选命令名，例如 build')
    parser.add_argument('--json', action='store_true', help='help 输出 JSON，方便 AI 读取')
    parser.add_argument('--path', help='Path relative to the authorized project')
    parser.add_argument('--discard-local', action='store_true', help='明确丢弃未保存缓冲区；需 --expected-revision')
    parser.add_argument('--expected-revision', help='document.read 返回的缓冲区 revision')
    parser.add_argument('--job', help='Build task ID; defaults to the latest task')
    parser.add_argument('--offset', type=int)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--start', type=int, help='First line (one-based)')
    parser.add_argument('--count', type=int, help='Number of lines')
    parser.add_argument('--engine', choices=['pdflatex', 'xelatex', 'lualatex'], default='xelatex')
    parser.add_argument('--wait', action='store_true', help='Wait for the submitted build')
    parser.add_argument('--timeout', type=float, default=300)
    args = parser.parse_args()
    if args.command == 'help':
        if args.topic and args.topic not in CLI_HELP['commands']:
            parser.error('未知帮助主题：'+args.topic)
        if args.json:
            # Built-in non-secret catalogue only. Never echo a session token.
            value=CLI_HELP if not args.topic else {'command':args.topic,**CLI_HELP['commands'][args.topic],
                'resultFields':CLI_HELP['resultFields'],'notes':CLI_HELP['notes']}
            print(json.dumps(value,ensure_ascii=False,indent=2))
        elif args.topic:
            item=CLI_HELP['commands'][args.topic]
            print(args.topic+' — '+item['summary'])
            for name,description in item.get('parameters',{}).items():print('  '+name+': '+description)
            if item.get('limits'):print('限制：'+item['limits'])
            print('\n示例：\n'+item['example'])
            print('\n注意：ok 表示请求成功；编译结果看 terminal、buildSucceeded 和 state。')
        else:
            parser.print_help()
            print('\n使用约定：\n'+'\n'.join('- '+note for note in CLI_HELP['notes']))
        return 0
    if args.topic or args.json:parser.error('主题名与 --json 仅用于 help')
    if not args.session:parser.error('执行应用命令需要 --session 连接文件')
    if (args.discard_local or args.expected_revision is not None) and args.command != 'document.reload':parser.error('重载参数仅用于 document.reload')
    if args.discard_local and not args.expected_revision:parser.error('--discard-local 必须同时提供 --expected-revision')
    try:
        session = json.loads(args.session.read_text(encoding='utf-8'))
        parameters = {name: getattr(args, name) for name in ('path','job','offset','limit','start','count') if getattr(args,name) is not None}
        if args.command=='document.reload':
            parameters['discardLocal']=args.discard_local
            if args.expected_revision is not None:parameters['expectedRevision']=args.expected_revision
        result = request(session, args.command, args.engine if args.command in ('build', 'build.clean') else None, **parameters)
        if args.command in ('build', 'build.clean') and args.wait and result.get('ok'):
            job = result['job']
            deadline = time.monotonic() + args.timeout
            while result.get('state') in ('queued', 'running'):
                if time.monotonic() >= deadline:
                    result = {'ok': False, 'error': 'client_timeout', 'job': job,
                              'note': 'Build may still be running; query status or cancel explicitly.'}
                    break
                time.sleep(0.3)
                result = request(session, 'job.status', job=job)
                if not result.get('ok'):
                    break
                if result.get('job') != job:
                    result = {'ok': False, 'error': 'job_replaced', 'job': job}
                    break
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get('ok') and result.get('buildSucceeded') is not False and result.get('state') not in ('failed', 'cancelled') else 1
    except (OSError, ValueError, KeyError) as error:
        # Never print the connection descriptor or token.
        print(json.dumps({'ok': False, 'error': type(error).__name__, 'message': str(error)}, ensure_ascii=False))
        return 2

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    sys.exit(main())
