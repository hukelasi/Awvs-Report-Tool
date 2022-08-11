#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import time
import requests
import socket
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

'''
# 升级:  不再限制读取文件时候的编码了,因为这样容易出错. 以后建议都这样( file, 'r') 就行了...
'''

try:
    with open('config.txt','r') as f:
        config = f.readlines()
        tarurl = config[0].replace('\n','')
        tarurl.strip()
        apikey = config[1].replace('\n','')
        apikey.strip()

        #print(tarurl,apikey)
except:
    print('您这是第一次安装吧,请先配置一下接口文件...')
    tarurl = input('请输入 Awvs 的网址:')
    tarurl.strip()
    apikey = input('请输入Awvs的key字符串:')
    apikey.strip()
    with open('config.txt','w') as f:
        f.write('{}\n{}'.format(tarurl,apikey))
    print('配置完毕,请重新运行本程序!')

    time.sleep(3)
    sys.exit()


# tarurl = "https://localhost:3443"
# apikey = "1986ad8c0a5b3df4d7028d5f3c06e936c8a31d080cb5a4231a3e258a9539e58e5"
headers = {"X-Auth": apikey, "Content-type": "application/json;charset=utf8"}


# 查看所有扫描任务
def show_scans():
    api_url = tarurl + '/api/v1/scans'
    r = requests.get(url=api_url, headers=headers, verify=False)
    res = r.json()['scans']
    # print(type(res))
    #
    # print(r.json())
    # print(res)
    m=input('\t显示最近几个任务 (默认10):')
    if not m:
        m=10
    else:
        m=int(m)
    n = 1
    for i in res:
        #print(i)
        a = i['target']['address']
        b = i['target']['description']
        c = i['current_session']['status']
        d = i['current_session']['start_date']
        d = d.split('.')[0]
        print('{}.[{}]\t{} {} \t{}'.format(n,c,a,b,d))
        n=n+1
        if n>m:
            break



# 查看所有目标
def show_targets():
    api_url = tarurl + '/api/v1/targets'
    r = requests.get(url=api_url, headers=headers, verify=False)
    res = r.json()
    #print(type(res))
    #print(res)

    #print('任务列表:', res['targets'])
    n = 1
    for i in res['targets']:
        #print(i)
        print(n, i['address'],'\t\t', i['description'],'\t\t', i['last_scan_session_status'])
        n=n+1


# 添加targets目标，获取target_id
def post_targets(url):
    api_url = tarurl + '/api/v1/targets'
    target_id_list = []
    # 此处是读取的描述 和 url 的顺序.
    for i in url:
        data = {
            "address": i[1],
            "description": i[0],
            "criticality": "10"
        }
        data_json = json.dumps(data)
        r = requests.post(url=api_url, headers=headers, data=data_json, verify=False)
        target_id = r.json().get("target_id")
        target_id_list.append(target_id)
    #print('target_id_list:', target_id_list)
    return target_id_list

# 添加scans
def scans(url):
    api_url = tarurl + '/api/v1/scans'
    for i in url:
        data = {
            "target_id": i,
            "profile_id": "11111111-1111-1111-1111-111111111111",
            "schedule":
                {"disable": False,
                 "start_date": None,
                 "time_sensitive": False
                 }
        }
        data_json = json.dumps(data)
        r = requests.post(url=api_url, headers=headers, data=data_json, verify=False)
    # target_id = r.json().get("target_id")
    # print(r.json)

# 获取scan_id，通过start_date可知，最新生成的为第一个
def scan_id(number):
    number=int(number)
    api_url = tarurl + '/api/v1/scans'
    scan_id_list = []
    r = requests.get(url=api_url, headers=headers, verify=False)
    for i in range(0, number):
        scan_id = r.json().get("scans")[i].get("scan_id")
        scan_id_list.append(scan_id)
    #print('scan_id_list:', scan_id_list)
    return scan_id_list

# 添加generate，并获取generate_id
def generate(url):
    api_url = tarurl + '/api/v1/reports'
    for i in url:
        data = {
            "template_id": "11111111-1111-1111-1111-111111111126",
            "source": {
                "list_type": "scans",
                "id_list": [i]
            }
        }
        data_json = json.dumps(data)
        r = requests.post(url=api_url, headers=headers, data=data_json, verify=False)
    #print(r.json)

def show_pdf(number):
    number = int(number)
    api_url = tarurl + '/api/v1/reports'
    r = requests.get(url=api_url, headers=headers, verify=False)

    baogao = r.json()['reports']

    for b in range(len(baogao)):
        i = baogao[b]
        f_name = i['source']['description']
        f_name = f_name.split(';')

        if i['status'] != 'completed':
            print('\t 报告还没生成完毕,请稍后再试...(当前任务: {} {})\n'.format(f_name[0],f_name[1]))
            time.sleep(3)
            break

        print('\t {3}.[{2}] {0} {1}'.format(f_name[0],f_name[1], i['status'],b))

        if b >= number-1:
            break

# 生成扫描报告,每次需要自己定义生成几个报告
def pdf(number):
    number = int(number)
    api_url = tarurl + '/api/v1/reports'
    #print(api_url)
    r = requests.get(url=api_url, headers=headers, verify=False)

    baogao = r.json()['reports']

    for b in range(len(baogao)):

        i = baogao[b]
        #print(i)    # i 是字典
        #print('下载地址:', i['download'][0]   ,   i['download'][1] )
        f_name = i['source']['description']
        f_name = f_name.split(';')

        if i['status'] != 'completed':
            print('\t报告还没生成完毕,请稍后再试...({}{})\n'.format(f_name[0],f_name[1]))
            time.sleep(3)
            break

        '''#print(f_name[0],f_name[1], i['status'])
        #print(f_name)  # 描述名是:f_name[1]
        #print('任务描述:', i['source']['description'])
        #print('任务编号:', i['source']['id_list'][0])
        '''
        taskid = i['source']['id_list'][0]
        pdf1 = i['download'][0]
        pdf2 = i['download'][1]

        r_html = requests.get(url=tarurl + pdf1, headers=headers, verify=False)
        with open(f"报告__{f_name[1]}_{taskid}.html", "wb") as code:
            code.write(r_html.content)
            code.close()


        # 暂时不生成 pdf,可以注释掉
        # r_html2 = requests.get(url=tarurl + pdf2, headers=headers, verify=False)
        # with open(f"报告__{f_name[1]}_{taskid}.pdf", "wb") as code:
        #     code.write(r_html2.content)
        #     code.close()

        if b >= number-1:
            break

def targets(file):
    url_list = []
    with open(file,'r') as f:
        urls = f.readlines()
    for i in urls:
        i = i.strip()
        i = i.strip('\n')
        i = i.split(',')
        #print(i)
        a = i[0].strip()
        b = i[1].strip()
        url_list.append( (a,b))
    #print(url_list)
    return url_list

def delete_targets():#删除全部扫描目标
    pas = input('\t此操作非常重要,删除后无法恢复. 请输入超级密码方可操作:')
    if pas != 'hello123':
        print('\t貌似密码不对哦, 您还是手工删除吧.\n')
        return False
    awvs_url = tarurl
    while 1:
        quer='/api/v1/targets'
        try:
            r = requests.get(awvs_url+quer, headers=headers, timeout=30, verify=False)
            result = json.loads(r.content.decode())
            if int(result['pagination']['count'])==0:
                print('已全部删除扫描目标，目前为空!!!\n')
                return 0
            for targetsid in range(len(result['targets'])):
                targets_id=result['targets'][targetsid]['target_id']
                targets_address = result['targets'][targetsid]['address']
                #print(targets_id,targets_address)
                try:
                    del_log=requests.delete(awvs_url+'/api/v1/targets/'+targets_id,headers=headers, timeout=30, verify=False)
                    if del_log.status_code == 204:
                        print(targets_address,' 删除目标成功')
                except Exception as e:
                    print(targets_address,e)
        except Exception as e:
            print(awvs_url+quer,e)

if __name__ == '__main__':
    print('''
~~~ Awvs 小工具  ver 0.4 ~~~\n
    1. 导入扫描任务\n
    2. 查看全部扫描任务\n
    3. 生成扫描报告\n
    4. 查看全部扫描报告\n
    5. 导出扫描报告\n
    6. 一键删除全部数据(慎)\n
    0. 退出\n
提示:按 h 随时回到帮助界面,按 0 退出本程序.

    ''')

    try:
       a = socket.gethostbyname('awvs101.idcmb.cn')
    except:
       print('缓存失败,请联系开发处理. 5 秒后退出!')
       time.sleep(6)
       sys.exit()

    flag = True
    try:
        while flag:
            id = input("请输入要执行的 id 号:")
            if not id:
                break

            if id =='2':
                show_scans()
                print('\n')
                pass

            elif id =='1':
                file = input('\t输入文本文件,必须是特定格式(描述,url):')
                file.strip()
                try:
                    url_list = targets(file)
                    print('\t成功导入 {}个 任务,请稍后...'.format(len(url_list)))
                except:
                    print('\t文本文件不存在哦...\n')
                    continue

                # 添加到targets队列
                target_id_list = post_targets(url_list)
                time.sleep(1)

                # 添加到scans队列
                scans(target_id_list)
                print('\t正在扫描!~~~\n')
                time.sleep(1)


            elif id == '3':
                num = input('\t输入数字,导出最新的多少个报告:')
                num.strip()
                scan_id_list = scan_id(num)
                generate(scan_id_list)
                time.sleep(1)
                print('\t正在生成报告,请稍后执行 "导出扫描报告".\n')
                time.sleep(3)

            elif id =='4':
                print('\t 显示最新生成的 10 份报告情况.')
                show_pdf(10)
                print('')

            elif id == '5':
                num = input('\t输入数字,导出最新的多少个报告:')
                num.strip()

                try:
                    pdf(num)
                    print('\t执行完毕!共导出了 {} 份报告~~~\n'.format(num))
                except:
                    print('\t报告还没生成完毕,请稍后执行"导出扫描报告"')
                time.sleep(3)

            elif id == '6':
                delete_targets()

            elif id =='0':
                flag = False

            else:
                continue
    except:
        print('执行失败,请检查 awvs 接口!')
        time.sleep(4)
        sys.exit()


