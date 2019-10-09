import os
import zipfile
import pymysql
import rarfile
import requests


def downloader(article_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Cookie': 'Hm_lvt_6dc7d7b0834abc6bcdc42ba4c22e18d0=1569810759,1569919717,1570246824,1570591910; Hm_lpvt_6dc7d7b0834abc6bcdc42ba4c22e18d0=1570591910; zmj77=1',
    }
    response = requests.get(f'http://down5.5156edu.com/showzipdown4.php?f_type1=2&id={article_id}', headers=headers)
    with open(f'{article_id}.zip', 'wb') as f:
        f.write(response.content)
    try:
        f = zipfile.ZipFile(f'{article_id}.zip')
        for file in f.namelist():
            f.extract(file, f'{article_id}/')
        f.close()
    except:
        f = rarfile.RarFile(f'{article_id}.zip')
        f.extractall(f'{article_id}/')
        f.close()
    os.remove(f'{article_id}.zip')
    os.remove(f'{article_id}/www.5156edu.com.txt')
    n = 0
    attachment_path_list = []
    for file in os.listdir(f'{article_id}/'):
        n += 1
        suffix = file.split('.')[-1]
        new_name = f'{article_id}/{n}.{suffix}'
        os.rename(f'{article_id}/{file}', new_name)
        file_path = '/data/wwwroot/Spider/attachment/' + new_name
        attachment_path_list.append(file_path)
    attachment_path = '|'.join(attachment_path_list)
    db = pymysql.connect("localhost", "root", "A123456", "edu", 50036)
    cursor = db.cursor()
    sql = "UPDATE resource SET attachment_path = %s WHERE article_id = %s" % (attachment_path, article_id)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    db.close()


if __name__ == '__main__':
    total_count = 0
    db = pymysql.connect("localhost", "root", "A123456", "edu", 50036)
    cursor = db.cursor()
    sql = "SELECT article_id FROM resource"
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        total_count += 1
        print(f'开始下载article_id为{row[0]}的附件，当前是第{total_count}个，共有{len(results)}个需要下载')
        downloader(row[0])
    db.close()
