import undetected_chromedriver as uc
options = uc.ChromeOptions()
options.add_argument("--user-data-dir=/tmp/test_dir")
try:
    driver = uc.Chrome(options=options)
    print("Success")
    driver.quit()
except Exception as e:
    print("Error:", e)
