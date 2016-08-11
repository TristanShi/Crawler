#-- coding=utf-8 --#
''' Tristan Shi '''


import time
from pyquery import PyQuery as pq
import random
import datetime
from pandas import DataFrame as df


# [1] 获取包含abs和reg信息的url, 并存储起来

isr_html_26_= {}
isr_url_1_26_ = {}  # 存储第一层遍历的网站url
isr_abs_url_26_ = {}    # 存储含abstract的url
isr_ref_url_26_ = {}    # 存储含references的url

def travel_save_url(domain):
 # 存储包含reference信息的网站url

    for i in xrange(1, 28):
        year = i
        for j in xrange(1, 5):
            issue = j
            if year==27 and issue==3:
                break

            url = domain + str(year) + "/" + str(issue)
            isr_ref_url_26_[url] = []
            isr_abs_url_26_[url] = []
            isr_url_1_26_[str(year) + str(issue)] = url

            isr_html_26_[str(year) + str(issue)] = pq(url)
            sleep_t = random.uniform(1.8, 20.2)  # 非整数休息时间, 给定一个1.8~20.2s之间的随机休息时间
            time.sleep(sleep_t)

            for item in isr_html_26_[str(year) + str(issue)]('table')('a.ref.nowrap'):
                temp = item.items()
                for tup in temp:
                    li = list(tup)
                    for ele in li:

                        if len(ele) > 25 and ele.find('ref') != -1:   # 获取包含abstract和references信息的页面
                            isr_ref_url_26_[url].append(ele)
                            isr_abs_url_26_[url].append(ele.replace('ref', 'abs'))


travel_save_url()

# [2] 存储包含abstract和references信息的pyquery
pyquery_ref_info_store_26 = {}
pyquery_abs_info_store_26 = {}


# 获取并存储单个url的pyquery_info
def store_pyquery_info(url, pyquery_info_store_26):
    sleep_t = random.uniform(3.2, 20.2)
    time.sleep(sleep_t)
    pyquery_info = pq(url)
    pyquery_info_store_26[url] = pyquery_info
    return


def store_all_ref_pyquery_info(isr_ref_url_26_, domain):
    # 只是为了给个进度条看看
    temp_rate = 0
    for i in xrange(26, 28):
        year = i
        for j in xrange(1, 5):
            issue = j
            if year==27 and issue==3:
                break
            url_1 = domain + str(year) + "/" + str(issue)

            for postfix in isr_ref_url_26_[url_1]:
                url_ref_2 = domain + postfix
                store_pyquery_info(url_ref_2, pyquery_ref_info_store_26)

                postfix_abs = postfix.replace('ref', 'abs')
                url_abs_2 = domain + postfix_abs
                store_pyquery_info(url_abs_2, pyquery_abs_info_store_26)

                temp_rate += 1
                print 'rate of progress: %d'%(temp_rate)
    return

# [3]  获得摘要和引用的所有信息, 格式化的保存起来

# 把日期转换为20100601这种格式
def date_trans(date):
    newDate = datetime.datetime.strptime(date, "%B %d, %Y")
    return newDate.strftime("%Y%m%d")

# 去掉空格



# 获得关于文章的大概信息用于匹配已有数据库, 以及references的信息, url为索引, 按格式获取
all_info_with_format_26 = []
ref_info_with_format_26 = []

def get_abs_with_format(url, each_pyquery_info, year, issue):
    each_abstract = {}
    # 先获得论文具体信息按url保存, 文章标题, 文章发布时间, 文章的pag_num, 文章的作者,
    abs_info = each_pyquery_info  # 以前是每次用pq来爬, 现在是读取
    each_abstract['url'] = url
    article_title = abs_info("div.publicationContentTitle")('h1').text()
    article_title = article_title
    each_abstract['Title'] = article_title

    # 对日期进行初步处理, 去掉前面没用的部分
    temp_date = abs_info("div.publicationContentEpubDate.dates").text()[18:]
    each_abstract['Date'] = date_trans(temp_date)

    # 对页码格式进行处理
    temp_page_num = abs_info('div.publicationContentPageRange').text()[20: ]
    each_abstract['Page_Num'] = temp_page_num.strip()

    # 获得作者姓名, 并将其放到list中
    for i in xrange(len(abs_info('div.header'))):
        Author_name = abs_info('div.header')[i].text
        each_abstract['Author%s'%(i+1)] = Author_name

    # 获得摘要信息
    temp_abstract = abs_info('div.abstractSection.abstractInFull').text()
    each_abstract['abstract'] = temp_abstract

    # 获得keywords
    temp_keywords = abs_info('div.abstractKeywords').text().replace('Keywords : ','')
    each_abstract['keywords'] = temp_keywords

    # 获得作者的信息
    for i in xrange(len(abs_info('div.contribAff'))):
        Author_info = abs_info('div.contribAff')[i].text
        each_abstract['Author%s_info' % (i + 1)] = Author_info

    # 获取其它信息
    each_abstract['Journal'] = 'Information Systems Research'
    each_abstract['year'] = year + 1989
    each_abstract['Vol'] = year
    each_abstract['Issue'] = issue
    temp_page_range = each_abstract['Page_Num']
    each_abstract['Page_Count'] = int(temp_page_range[temp_page_range.find('-') + 1:]) \
                                                       - \
                                                       int(temp_page_range[:temp_page_range.find('-')]) + 1

    return each_abstract

def get_ref_with_format(url, each_pyquery_info):

    ref = each_pyquery_info
    for i in xrange(len(ref('div.hlFld-Fulltext')('tr'))):
        m = i + 1  # 实际情况是从B1开始
        ref_html_text = ref('div.hlFld-Fulltext')("tr#B%d" % m).text()
        ref_html_content = ref('div.hlFld-Fulltext')("tr#B%d" % m).html()
        ref_info_with_format_26.append(format_ref(ref_html_content, ref_html_text, url))

    return

# 转换references的格式
def format_ref(ref_html_content, ref_html_text, url):
    each_reference = {}
    each_reference['url'] = url
    each_reference['total_reference'] = ref_html_text
    # 先替换掉没用的信息
    temp1 = ref_html_content.replace('<td class="refnumber"> </td><td valign="top">', '')
    temp2 = temp1.replace('<span class="NLM_given-names">', '')

    author_name = ref_html_text[:ref_html_text.find('(')]
    each_reference['Author'] = author_name

    NLM_journal_vol_issue = temp2[temp2.find("</i>") + 5: temp2.find(':<s')]# 格式'27(4)' ?????修改
    if len(NLM_journal_vol_issue) <=  7:
        each_reference['NLM_journal_vol_issue'] = NLM_journal_vol_issue
    else:
        each_reference['NLM_journal_vol_issue'] = ''

    # 获取其它信息
    temp_reference = pq(temp1)
    each_reference['NLM_given_names'] = temp_reference('span.NLM_given-names').text()
    each_reference['NLM_year'] = temp_reference('span.NLM_year').text()     # year
    each_reference['NLM_article_title'] = temp_reference('span.NLM_article-title').text()   # title
    each_reference['NLM_journal_name'] = temp_reference('i').text()  # journal name
    each_reference['NLM_conf_info'] = temp_reference('span.NLM_conf-name').text() \
                                      + \
                                      temp_reference('span.NLM_conf-loc').text()
    each_reference['NLM_edition'] = temp_reference('span.NLM_edtion').text()
    each_reference['NLM_publisher-name'] = temp_reference('span.NLM_publisher-name').text()
    each_reference['NLM_publisher-loc'] = temp_reference('span.NLM_publisher-loc').text()
    # 有些是没有page_num, 没有的话就写为空
    if temp_reference('span.NLM_fpage').text() != '':
        each_reference['NLM_journal_page_num'] = temp_reference('span.NLM_fpage').text() \
                                                 + '-' + \
                                                 temp_reference('span.NLM_lpage').text()
    else:
        each_reference['NLM_journal_page_num'] = ''
    return each_reference




# 全部信息爬取
def get_all_info(isr_ref_url_26_, pyquery_abs_info_store_26, pyquery_ref_info_store_26):
    domain = 'domain_url'
    for i in xrange(26, 28):
        year = i
        for j in xrange(1, 5):
            issue = j
            url_1 = "domain_url" + str(year) + "/" + str(issue)
            if year==27 and issue==3:
                break


            for postfix in isr_ref_url_26_[url_1]:
                url_ref_2 = domain + postfix
                postfix_abs = postfix.replace('ref', 'abs')
                url_abs_2 = domain + postfix_abs
                each_pyquery_info = pyquery_abs_info_store_26[url_abs_2]


                all_info_with_format_26.append(get_abs_with_format(url_ref_2, each_pyquery_info, year, issue))  # 获取按格式的引用信息 ref_info_with_format


            for postfix in isr_ref_url_26_[url_1]:
                url_ref_2  = domain + postfix
                each_pyquery_info = pyquery_ref_info_store_26[url_ref_2]

                get_ref_with_format(url_ref_2, each_pyquery_info)

    return

# [4] 存储

def to_crawler_excel(df, name, path):
    return df.to_excel(''.join(''.join([path, name ,'.xls'])))

all_info_with_format_26_pd_col = '[col]'    # col信息
all_info_with_format_26_pd = df(all_info_with_format_26, columns=all_info_with_format_26_pd_col)
all_info_with_format_26_pd.index += 1
to_crawler_excel(all_info_with_format_26_pd, 'all_info_with_format_26_pd')


ref_info_format_26_pd_col = '[col]'
ref_info_format_26_pd = df(ref_info_with_format_26, columns=ref_info_format_26_pd_col)
ref_info_format_26_pd.index += 1
to_crawler_excel(ref_info_format_26_pd, 'ref_info_format_26_pd')


