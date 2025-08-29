#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟浏览器打开Google首页
使用Selenium WebDriver模拟真实浏览器行为
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import random
from urllib.parse import urlparse, parse_qs


class GoogleBrowserSimulator:
    def __init__(self, headless=False):
        """
        初始化浏览器模拟器
        
        Args:
            headless (bool): 是否使用无头模式（不显示浏览器窗口）
        """
        self.chrome_options = Options()
        
        # 设置浏览器选项
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 设置用户代理
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        if headless:
            self.chrome_options.add_argument('--headless')
        
        self.driver = None

    def get_url_params(self, url, param_name):
        """
        获取URL参数
        """
        return parse_qs(urlparse(url).query)[param_name][0] if param_name in parse_qs(urlparse(url).query) else None
        
    def start_browser(self):
        """启动浏览器"""
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            # 执行JavaScript来隐藏webdriver属性
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("浏览器启动成功")
            return True
        except Exception as e:
            print(f"浏览器启动失败: {e}")
            return False
    
    def open_google(self):
        """
        打开Google首页
        
        Returns:
            dict: 页面信息
        """
        if not self.driver:
            print("浏览器未启动")
            return None
        
        try:
            print("正在打开Google首页...")
            self.driver.get("https://www.google.com/")
            
            # 等待页面加载完成
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            
            # 获取页面信息
            page_info = self._get_page_info()
            
            print("Google首页加载完成")
            return page_info
            
        except Exception as e:
            print(f"打开Google首页失败: {e}")
            return None
    
    def _get_page_info(self):
        """
        获取页面信息
        
        Returns:
            dict: 页面信息
        """
        page_info = {
            'title': self.driver.title,
            'url': self.driver.current_url,
            'elements': {}
        }
        
        try:
            # 获取搜索框
            search_box = self.driver.find_element(By.NAME, "q")
            page_info['elements']['search_box'] = {
                'placeholder': search_box.get_attribute('placeholder'),
                'value': search_box.get_attribute('value')
            }
            
            # 获取导航链接
            nav_links = []
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='google.com']")
            for element in nav_elements[:10]:  # 限制数量
                try:
                    nav_links.append({
                        'text': element.text,
                        'href': element.get_attribute('href')
                    })
                except:
                    continue
            
            page_info['elements']['navigation_links'] = nav_links
            
            
        except Exception as e:
            print(f"获取页面信息时出错: {e}")
        
        return page_info
    
    def search_keyword(self, keyword, num_pages=3):
        """
        在Google中搜索关键词，爬取多页结果
        
        Args:
            keyword (str): 搜索关键词
            num_pages (int): 要爬取的页数
            
        Returns:
            list: 搜索结果信息
        """
        if not self.driver:
            print("浏览器未启动")
            return None
        
        all_results = []
        
        try:
            # 找到搜索框并输入关键词
            search_box = self.driver.find_element(By.NAME, "q")
            search_box.clear()
            search_box.send_keys(keyword)
            
            # 提交搜索
            search_box.submit()
            
            # 等待搜索结果加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            
            # 爬取多页结果
            for page in range(num_pages):
                # print(f"正在爬取第 {page + 1} 页...")
                
                # 获取当前页搜索结果
                page_results = self._get_search_results()
                all_results.extend(page_results)
                
                # 如果不是最后一页，点击下一页
                if page < num_pages - 1:
                    try:
                        # 查找下一页按钮
                        next_button = self.driver.find_element(By.ID, "pnnext")
                        next_button.click()
                        
                        # 等待新页面加载
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.ID, "search"))
                        )
                        
                        # 随机延迟
                        time.sleep(random.uniform(2, 4))
                        
                    except Exception as e:
                        print(f"无法找到下一页按钮或点击失败: {e}")
                        break
            
            # print(f"搜索 '{keyword}' 完成，总共找到 {len(all_results)} 个结果")
            return all_results
            
        except Exception as e:
            print(f"搜索失败: {e}")
            return None
    
    def _get_search_results(self):
        """
        获取搜索结果
        
        Returns:
            list: 搜索结果列表
        """
        results = []
        
        try:
            # 查找所有的 a 标签
            # result_elements = self.driver.find_elements(By.CSS_SELECTOR, "a")
            # 获取所有 a 标签
            result_elements = self.driver.find_elements(By.TAG_NAME, "a")

            for element in result_elements: 
                href = element.get_attribute('href')
                # get url params value vipCode

                if href and 'weex' in href:
                 vipCode = self.get_url_params(href, 'vipCode')
                 if vipCode:
                  results.append({
                      'url': element.get_attribute('href'),
                      'vipCode': vipCode
                  })

            
            
        except Exception as e:
            print(f"获取搜索结果时出错: {e}")
        
        return results
    
    def save_results(self, results, filename='google_search_results.json'):
        """
        保存结果到JSON文件
        
        Args:
            results (dict): 结果数据
            filename (str): 文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到 {filename}")
        except Exception as e:
            print(f"保存结果失败: {e}")
    
    def close_browser(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")


def main():
    """主函数"""
    print("Google浏览器模拟器")
    print("=" * 50)
    
    # 创建浏览器模拟器实例
    simulator = GoogleBrowserSimulator(headless=False)  # 设置为True可以隐藏浏览器窗口
    
    try:
        # 启动浏览器
        if not simulator.start_browser():
            return
        
        # 打开Google首页
        page_info = simulator.open_google()
        if page_info:
            print(f"页面标题: {page_info['title']}")
            print(f"页面URL: {page_info['url']}")
            # print(f"截图已保存: {page_info.get('screenshot', 'N/A')}")
        
        # 等待用户查看
        
        # 搜索关键词，爬取前2页
        search_results = simulator.search_keyword("weex", num_pages=2)

        # 去重, vipCode 相同的只保留一个
        # search_results = list(dict.fromkeys(result['vipCode'] for result in search_results))
        res = {}

        for result in search_results:
            if result['vipCode'] not in res:
                res[result['vipCode']] = result
        
        search_results = list(res.values())


        print("-"*100)
        # 显示搜索结果
        if search_results:
            print(f"总共找到 {len(search_results)} 个包含vipCode的链接")
            try:
                for result in search_results:
                    print("-"*100)
                    print(f"vipCode: {result['vipCode']}")
                    print(f"URL: {result['url']}")
            except Exception as e:
                print(f"获取搜索结果时出错: {e}")

           
            
           
        else:
            print("未找到包含vipCode的链接")
        
        # 等待用户查看
        # print("\n搜索完成，按回车键关闭浏览器...")
        # input()
        
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"程序执行出错: {e}")
    finally:
        # 关闭浏览器
        simulator.close_browser()


if __name__ == "__main__":
    main()
