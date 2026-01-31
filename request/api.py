# encoding=utf-8

from config import php_ip


update_json_status = "{}/status/update".format(php_ip)
save = "{}/video/save".format(php_ip)
save_image = "{}/image/save".format(php_ip)
water_rule = php_ip + "/rule/get"
get_rule = php_ip + "/rule/get"
check_cat_and_subcat = php_ip + "/category/subcategory/exsit"
get_category = "{}/category/english".format(php_ip)
get_user_key = "{}/key/get".format(php_ip)
# 通过分类获取项目， 通过项目id获取服务器id， 然后获取服务器信息
get_server_info = php_ip + "/server/info/{}"
upload_callback = php_ip +"/post/url/{}"
get_user_by_ftp_user = php_ip +"/get/user/by/ftpuser"
exsit_identifier = php_ip +"/identifier/exsits?identifier="
get_project = php_ip +"/get/project/dir"
# 获取资源机器信息
get_resource = php_ip +"/resource/get"