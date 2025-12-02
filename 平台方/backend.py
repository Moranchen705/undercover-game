"""
后端服务器模块
提供RESTful API接口，处理游戏方的请求
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from game_logic import GameLogic, GameStatus
from datetime import datetime
import os
import threading
import socket

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 管理员令牌（主持方专用）
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "host-secret")

# 全局游戏逻辑实例
game = GameLogic()

# 线程锁，保证线程安全
game_lock = threading.Lock()


def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def _require_admin():
    """校验主持方权限"""
    header_token = request.headers.get("X-Admin-Token", "")
    return header_token == ADMIN_TOKEN


def _admin_forbidden_response():
    return make_response({}, 403, '无权限：需要主持方令牌')


def make_response(data=None, code=200, message="ok"):
    payload = {
        "code": code,
        "message": message,
        "data": data or {}
    }
    return jsonify(payload), code


@app.route('/api/register', methods=['POST'])
def register():
    """游戏方注册接口"""
    data = request.json
    group_name = data.get('group_name') or data.get('group_id', '')
    group_name = group_name.strip() if isinstance(group_name, str) else ''
    
    if not group_name:
        return make_response({}, 400, '组名不能为空')
    
    with game_lock:
        success = game.register_group(group_name)
        if success:
            return make_response({
                'group_name': group_name,
                'total_groups': len(game.groups)
            }, 200, '注册成功')
        else:
            return make_response({}, 400, '注册失败：组名已存在或已达到最大组数(5组)')


@app.route('/api/game/start', methods=['POST'])
def start_game():
    """开始游戏接口（主持方调用）"""
    if not _require_admin():
        return _admin_forbidden_response()
    data = request.json
    undercover_word = data.get('undercover_word', '').strip()
    civilian_word = data.get('civilian_word', '').strip()
    
    if not undercover_word or not civilian_word:
        return make_response({}, 400, '词语不能为空')
    
    with game_lock:
        success = game.start_game(undercover_word, civilian_word)
        if success:
            return make_response({
                'undercover_group': game.undercover_group,
                'groups': {name: info['role'] for name, info in game.groups.items()}
            }, 200, '游戏已开始')
        else:
            return make_response({}, 400, '无法开始游戏：游戏状态不正确或没有注册的组')


@app.route('/api/game/round/start', methods=['POST'])
def start_round():
    """开始新回合接口（主持方调用）"""
    if not _require_admin():
        return _admin_forbidden_response()
    with game_lock:
        order = game.start_round()
        if order:
            return make_response({
                'round': game.current_round,
                'order': order
            }, 200, '回合已开始')
        else:
            return make_response({}, 400, '无法开始回合：游戏状态不正确或活跃组数不足')


@app.route('/api/describe', methods=['POST'])
def submit_description():
    """提交描述接口（游戏方调用）"""
    data = request.json
    group_name = data.get('group_name', '').strip()
    description = data.get('description', '').strip()
    
    if not group_name or not description:
        return make_response({}, 400, '组名和描述不能为空')
    
    with game_lock:
        success = game.submit_description(group_name, description)
        if success:
            # 获取当前描述列表
            current_descriptions = game.descriptions.get(game.current_round, [])
            return make_response({
                'round': game.current_round,
                'total_descriptions': len(current_descriptions)
            }, 200, '描述提交成功')
        else:
            # 检查具体失败原因
            if game.game_status != GameStatus.DESCRIBING:
                return make_response({}, 400, '描述提交失败：当前不在描述阶段')
            if group_name in [d['group'] for d in game.descriptions.get(game.current_round, [])]:
                return make_response({}, 400, '描述提交失败：已提交过描述')
            # 可能是超时
            return make_response({}, 400, '描述提交失败：已超时（3秒限制）、组名无效或游戏状态不正确')


@app.route('/api/vote', methods=['POST'])
def submit_vote():
    """提交投票接口（游戏方调用）"""
    try:
        data = request.json
        print(f"[投票请求] 收到投票请求: {data}")  # 调试日志
        if not data:
            print("[投票请求] 错误: 请求数据为空")
            return make_response({}, 400, '请求数据为空')
        
        voter_group = data.get('voter_group', '').strip()
        target_group = data.get('target_group', '').strip()
        
        print(f"[投票请求] 投票者: {voter_group}, 目标: {target_group}")
        
        if not voter_group or not target_group:
            print("[投票请求] 错误: 投票者和被投票者不能为空")
            return make_response({}, 400, '投票者和被投票者不能为空')
        
        with game_lock:
            # 防御性检查：确保game对象和关键属性存在
            if game is None:
                return make_response({}, 500, '投票提交失败：游戏对象未初始化')
            if not hasattr(game, 'groups') or game.groups is None:
                return make_response({}, 500, '投票提交失败：游戏组数据未初始化')
            if not hasattr(game, 'eliminated_groups') or not isinstance(game.eliminated_groups, list):
                return make_response({}, 500, '投票提交失败：淘汰组数据异常')
            if not hasattr(game, 'votes') or game.votes is None:
                return make_response({}, 500, '投票提交失败：投票数据未初始化')
            if not hasattr(game, 'current_round') or game.current_round is None:
                return make_response({}, 500, '投票提交失败：当前回合数异常')
            
            # 确保current_round是有效的整数
            if not isinstance(game.current_round, int) or game.current_round < 0:
                return make_response({}, 500, f'投票提交失败：当前回合数无效（{game.current_round}）')
            
            # 先检查游戏状态，如果不是投票阶段，尝试自动转换
            if game.game_status == GameStatus.DESCRIBING:
                # 检查是否应该自动进入投票阶段
                if not hasattr(game, 'describe_order') or game.describe_order is None:
                    game.describe_order = []
                active_groups_in_order = [g for g in game.describe_order if g not in game.eliminated_groups]
                submitted_count = len(game.descriptions.get(game.current_round, []))
                if submitted_count >= len(active_groups_in_order):
                    game.game_status = GameStatus.VOTING
                elif game.round_start_time:
                    try:
                        elapsed_time = (datetime.now() - game.round_start_time).total_seconds()
                        max_time = len(active_groups_in_order) * game.description_timeout
                        if elapsed_time > max_time:
                            game.game_status = GameStatus.VOTING
                    except Exception as e:
                        # 时间计算出错，记录但不影响流程
                        print(f"时间计算错误: {e}")
            
            # 详细检查失败原因（在调用submit_vote之前）
            if game.game_status != GameStatus.VOTING:
                return make_response({}, 400, '投票提交失败：当前不在投票阶段（状态：' + game.game_status.value + '）')
            
            # 确保当前回合的投票字典存在
            if game.current_round not in game.votes:
                game.votes[game.current_round] = {}
            
            # 检查是否已经投过票了
            current_round_votes = game.votes.get(game.current_round, {})
            print(f"[投票请求] 当前回合: {game.current_round}, 已投票记录: {current_round_votes}")
            if voter_group in current_round_votes:
                print(f"[投票请求] 错误: {voter_group} 已投过票，目标: {current_round_votes.get(voter_group)}")
                return make_response({}, 400, '投票提交失败：已投过票')
            if voter_group == target_group:
                return make_response({}, 400, '投票提交失败：不能投自己')
            if voter_group in game.eliminated_groups:
                return make_response({}, 400, '投票提交失败：投票者已淘汰')
            if target_group in game.eliminated_groups:
                return make_response({}, 400, '投票提交失败：被投票者已淘汰')
            if voter_group not in game.groups:
                return make_response({}, 400, f'投票提交失败：投票者组名无效（注册的组：{list(game.groups.keys())}）')
            if target_group not in game.groups:
                return make_response({}, 400, f'投票提交失败：目标组名无效（注册的组：{list(game.groups.keys())}）')
            active_groups = [g for g in game.groups.keys() if g not in game.eliminated_groups]
            if target_group not in active_groups:
                return make_response({}, 400, f'投票提交失败：目标组不在存活组中（存活组：{active_groups}，目标：{target_group}）')
            
            # 所有检查都通过，调用submit_vote
            success = game.submit_vote(voter_group, target_group)
            if success:
                print(f"[投票请求] 成功: {voter_group} 投票给 {target_group}")
                return make_response({}, 200, '投票提交成功')
            else:
                # 如果submit_vote返回False，但前面的检查都通过了，说明有内部逻辑问题
                print(f"[投票请求] 错误: submit_vote返回False，但前面的检查都通过了")
                return make_response({}, 400, f'投票提交失败：内部逻辑错误（请检查游戏状态和投票记录）')
    except KeyError as e:
        # 处理KeyError异常
        import traceback
        error_detail = f"KeyError: {str(e)}"
        traceback.print_exc()
        return make_response({}, 500, f'投票提交失败：数据访问错误 - {error_detail}')
    except AttributeError as e:
        # 处理AttributeError异常
        import traceback
        error_detail = f"AttributeError: {str(e)}"
        traceback.print_exc()
        return make_response({}, 500, f'投票提交失败：属性访问错误 - {error_detail}')
    except Exception as e:
        # 捕获所有其他异常，避免500错误
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}"
        traceback.print_exc()
        return make_response({}, 500, f'投票提交失败：服务器内部错误 - {error_detail}')


@app.route('/api/game/voting/process', methods=['POST'])
def process_voting():
    """处理投票结果接口（主持方调用）"""
    if not _require_admin():
        return _admin_forbidden_response()
    with game_lock:
        result = game.process_voting_result()
        if 'error' in result:
            return make_response(result, 400, result.get('error', '投票处理失败'))
        return make_response(result, 200, '投票结果已生成')


@app.route('/api/game/state', methods=['GET'])
def get_game_state():
    """获取游戏状态接口"""
    if not _require_admin():
        return _admin_forbidden_response()
    with game_lock:
        state = game.get_game_state()
        return make_response(state)


@app.route('/api/status', methods=['GET'])
def public_status():
    """游戏方公共状态接口"""
    with game_lock:
        status = game.get_public_status()
        return make_response(status)


@app.route('/api/result', methods=['GET'])
def public_result():
    """最近一次投票结果"""
    with game_lock:
        result = game.get_last_result()
        if not result:
            return make_response({}, 404, '当前暂无投票结果')
        return make_response(result)


@app.route('/api/descriptions', methods=['GET'])
def get_descriptions():
    """获取当前回合的所有描述（游戏方调用）"""
    with game_lock:
        descriptions = game.get_current_round_descriptions()
        return make_response({
            'round': game.current_round,
            'descriptions': descriptions
        })


@app.route('/api/word', methods=['GET'])
def get_word():
    """获取词语接口（游戏方调用，仅返回自己的词语）"""
    group_name = request.args.get('group_name', '').strip()
    
    if not group_name:
        return make_response({}, 400, '组名不能为空')
    
    with game_lock:
        word = game.get_group_word(group_name)
        if word:
            return make_response({'word': word})
        else:
            return make_response({}, 404, '未找到该组的词语或游戏未开始')


@app.route('/api/game/reset', methods=['POST'])
def reset_game():
    """重置游戏接口（主持方调用）"""
    if not _require_admin():
        return _admin_forbidden_response()
    with game_lock:
        game.reset_game()
        return make_response({}, 200, '游戏已重置')


@app.route('/api/report', methods=['POST'])
def report_issue():
    """异常上报接口（游戏方调用）"""
    data = request.json or {}
    group_name = data.get('group_name') or data.get('group_id', '')
    group_name = group_name.strip() if isinstance(group_name, str) else ''
    report_type = data.get('type', 'general').strip() or 'general'
    detail = data.get('detail', '').strip()

    if not detail:
        return make_response({}, 400, 'detail不能为空')

    with game_lock:
        report_entry = game.add_report(group_name, report_type, detail)

    return make_response({
        'ticket': report_entry['ticket'],
        'recorded_at': report_entry['time']
    }, 200, '异常已记录')


@app.route('/api/groups', methods=['GET'])
def get_groups():
    """获取所有注册的组接口"""
    with game_lock:
        groups_info = []
        for name, info in game.groups.items():
            groups_info.append({
                'name': name,
                'registered_time': info['registered_time'],
                'eliminated': name in game.eliminated_groups
            })
        return make_response({
            'groups': groups_info,
            'total': len(groups_info)
        })


@app.errorhandler(Exception)
def handle_exception(e):
    """全局异常处理"""
    import traceback
    error_detail = f"{type(e).__name__}: {str(e)}"
    traceback.print_exc()
    return make_response({}, 500, f'服务器内部错误 - {error_detail}')


if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"=" * 50)
    print(f"谁是卧底 - 主持方平台")
    print(f"=" * 50)
    print(f"服务器启动中...")
    print(f"本地访问: http://127.0.0.1:5000")
    print(f"局域网访问: http://{local_ip}:5000")
    print(f"=" * 50)
    print(f"请确保游戏方能够访问上述IP地址")
    print(f"=" * 50)
    
    # 运行服务器，允许局域网访问
    app.run(host='0.0.0.0', port=5000, debug=True)

