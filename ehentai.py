import sys
import requests
from lxml import etree
import os
import re
import time
from multiprocessing import Pool
#from requests.cookies import RequestsCookieJar


def single_page(inputurl,inputhead,fileurl,picscount):
	etreepicpagestart = time.time()
	picpage = etree.HTML(requests.get(inputurl,headers=inputhead).text)
	etreepicpageend = time.time()
	print("获取图片页面信息耗时:"+str(etreepicpageend - etreepicpagestart))

	picurlstart = time.time()
	picurl = picpage.xpath('//img[@id="img"]/@src')
	pictype = ""
	if(picurl[0][-3:] == "jpg"):
		pictype = "jpg"
	elif(picurl[0][-3:] == "gif"):
		pictype = "gif"
	elif(picurl[0][-3:] == "png"):
		pictype = "png"
	elif(picurl[0][-4:] == "webm"):
		pictype = "webm"
	else:
		pictype = "jpg"
	picurlend = time.time()
	print("检索图片url耗时："+str(picurlend - picurlstart))

	# picbytestart = time.time()
	while True:
		#print(picurl[0])
		picbyte = requests.get(picurl[0],headers=inputhead).content
		if len(picbyte) > 1000:
			#print('#################OUT!!!!!')
			break
		time.sleep(5)
	# picbyteend = time.time()
	# print("获取图片耗时："+str(picbyteend - picbytestart))
	print('&&&&&&&&&&&&&&&&&&&&&&')
	picstart = time.time()
	print(fileurl+"\\"+str(picscount)+"."+pictype)
	f = open(fileurl+"\\"+str(picscount)+"."+pictype,"wb")
	f.write(picbyte)
	picend = time.time()
	print(str(picscount)+"张已完成,耗时："+str(picend - picstart))
	
	f.close()


def downloadpics(inputurl,inputhead,is_single=False):
	content_warning = False
	is_single_pages = []
	getchildstart = time.time()
	print("In!")
	#获取子页面并转换为etree格式
	mainpage_response = requests.get(inputurl,headers=inputhead)
	page = etree.HTML(mainpage_response.text)
	#cookie = mainpage_response.cookies
	getchildend = time.time()
	print("获取子页面完成 耗时："+str(getchildend - getchildstart))
	if len(page.xpath('//body/div/h1')) > 0:
		print('Content Warning')
		content_warning = True
		temp_inputurl = inputurl + "/?nw=session"
		warn_session = requests.session()
		temp_page = warn_session.get(temp_inputurl,headers=inputhead)
		
		page = etree.HTML(temp_page.text)
		_cookies = warn_session.cookies
		print(_cookies)
		for cookie in _cookies:
			print(cookie)
		


	#找出本页面的title

	title = page.xpath('//h1[@id="gn"]')



	#以title为名创建文件夹

	makedirstart = time.time()
	getfileurlstart = time.time()
	#print(title)
	fileurl = "D:/mypy/Manga/"+re.sub("[|]?[/]?[<]?[>]?[\\\\]?[:]?[\"]?[*]?[\?]?","",title[0].text)
	getfileurlend = time.time()
	print("处理文件夹名称耗时："+str(getfileurlend - getfileurlstart))

	if os.path.exists(fileurl):
		print(fileurl+"已存在")
		print("自动跳过")
	else:
		os.mkdir(fileurl)
		makedirend = time.time()
		print("已创建："+title[0].text)
		print("创建文件夹耗时："+str(makedirend - makedirstart))

	#找出子页面图片共有多少页
	#if content_warning:

	pagenum = int(page.xpath('//table[@class="ptt"]/tr/td[last()-1]/a/text()')[0])


	picscount = 1


	pagelist = [inputurl]


	print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"+str(pagenum))
	if pagenum > 1:
#		if content_warning:
#			for n in range(1,pagenum):
#				pagelist.append(inputurl+'/?p='+str(n))
		for n in range(1,pagenum):
			pagelist.append(inputurl+'/?p='+str(n))

	for pageurl in pagelist:
		print("in pagelist!")
		if content_warning:
			page = etree.HTML(warn_session.get(pageurl,headers=inputhead,cookies=_cookies).text)
		else:
			page = etree.HTML(requests.get(pageurl,headers=inputhead).text)
		print("page loaded!")
		#if len(page.xpath('//body/div/h1')) > 0:
		#	page = etree.HTML(requests.get(pageurl+"/?nw=session",headers=inputhead).text)
		print("pageurl = "+pageurl)
		getchildpicstart = time.time()
		#找出子页面中的每页图片子页面的url并转换成列表
		mangapage = page.xpath('//div[@class="gdtm"]/div/a/@href')

		getchildpicend = time.time()
		print("获取子页面图片url完成 耗时："+str(getchildpicend - getchildpicstart))
		for ii in mangapage:
			print(ii)
		downloadpicsstart = time.time()
		counter = 1
		print(counter)

		for m in mangapage:
			if is_single == True:
				is_single_pages.append(m)
			else:
				single_page(m,inputhead,fileurl,picscount)
				picscount += 1
		downloadpicsend = time.time()
		print("下载图片总耗时："+str(downloadpicsend - downloadpicsstart))
	if is_single == True:
		is_single_pages.append(fileurl)
		return is_single_pages


def searchlink(words,option):
    search = ""
    if len(words) > 1:
        #for search options except the last one
        for item in words[:-1]:
            item = item.split()
            if len(item) > 1:
                search += option+'%3A"'
                for i in item[:-1]:
                    search += i+'+'
                search += item[-1:][0]+'%24"+'
            elif len(item) == 1:
                search += option+'%3A'+item[0]+'%24+'
        #for the last search option
        item = words[-1:][0].split()
        if len(item) > 1:
            search += option+'%3A"'
            for i in item[:-1]:
                search += i+'+'
            search += item[-1:][0]+'%24"'
        elif len(item) == 1:
            search += option+'%3A'+item[0]+'%24'
    elif len(words) == 1:
        item = words[0].split()
        if len(item) > 1:
            search += option+'%3A"'
            for i in item[:-1]:
                search += i+'+'
            search += item[-1:][0]+'%24"'
        elif len(item) == 1:
            search += option+'%3A'+item[0]+'%24'

    return search


if __name__ == '__main__':
	#header
	head = {
	    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
	}
	p = Pool(32)
	searchwords = ""
	argv = sys.argv
	start = time.time()

	if argv[1][:5] == 'http:' or argv[1][:6] == 'https:':
		is_s = True
		re_list = downloadpics(argv[1],head,is_s)
		picscount = 1
		for u in re_list[:-1]:
			print(u)
			p.apply_async(single_page, args=(u,head,re_list[-1],picscount))
			picscount += 1

		print("Waiting for all subprocesses done...")
		p.close()
		print("################################################P.CLOSE()#####################################")
		p.join()
		end = time.time()
		print("=========================全程耗时："+str(end - start))
		print("All Done!")

		
	else:
		# search = input("搜索内容：")
		print("type your search, use ',' to devide them")
		parody = input("parody:").split(',')
		character = input("character:").split(',')
		group = input("group:").split(',')
		artist = input("artist:").split(',')
		male = input("male:").split(',')
		female = input("female:").split(',')
		misc = input("misc:").split(',')


		pages = int(input(("how many pages：")))

		if len(parody[0]) > 1:
			searchwords += searchlink(parody,"parody")+'+'
		if len(character[0]) > 1:
			searchwords += searchlink(character,"character")+'+'
		if len(group[0]) > 1:
			searchwords += searchlink(group,"group")+'+'
		if len(artist[0]) > 1:
			searchwords += searchlink(artist,"artist")+'+'
		if len(male[0]) > 1:
			searchwords += searchlink(male,"male")+'+'
		if len(female[0]) > 1:
			searchwords += searchlink(female,"female")+'+'
		if len(misc[0]) > 1:
			searchwords += searchlink(misc,"misc")+'+'

	  				

		for i in range(pages):
			if i == 0:
				#主站url
				url = 'https://e-hentai.org/?f_doujinshi=1&f_manga=1&f_artistcg=1&f_gamecg=1&f_western=1&f_non-h=1&f_imageset=1&f_cosplay=1&f_asianporn=1&f_misc=1&f_search='+searchwords+'&f_apply=Apply+Filter'
			else:
				url = 'https://e-hentai.org/?page='+str(i)+'&f_doujinshi=1&f_manga=1&f_artistcg=1&f_gamecg=1&f_western=1&f_non-h=1&f_imageset=1&f_cosplay=1&f_asianporn=1&f_misc=1&f_search='+searchwords+'&f_apply=Apply+Filter'
			
			#网站主页
			print("开始获取主页信息...")
			mainpagestart = time.time()
			mainpage = etree.HTML(requests.get(url, headers=head).text)
			mainpageend = time.time()
			print("Done! 耗时："+str(mainpageend - mainpagestart))
			#对主页内容分析并找出子页面url
			#找出子页面url
			childurlstart = time.time()
			url = mainpage.xpath('//div[@class="it5"]/a/@href')
			childurlend = time.time()
			print("检索子页面url完成 耗时："+str(childurlend - childurlstart))
			#对每一个子页面url进行处理
			if url:
				for u in url[:]:
					print(u)
					p.apply_async(downloadpics, args=(u,head))
			else:
				print("总页数为"+str(i+1)+"页")
				break
		print("Waiting for all subprocesses done...")
		p.close()
		print("################################################P.CLOSE()#####################################")
		p.join()
		end = time.time()
		print("=========================全程耗时："+str(end - start))
		print("All Done!")
			
