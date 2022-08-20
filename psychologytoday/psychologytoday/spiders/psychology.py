import scrapy
from scrapy import Request


class PsychologySpider(scrapy.Spider):
    name = 'psychology'
    allowed_domains = ['www.psychologytoday.com']
    start_urls = ['https://www.psychologytoday.com/au']
    custom_settings = {'ROBOTSTXT_OBEY': False, 'LOG_LEVEL': 'INFO',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': 10,
                       'RETRY_TIMES': 5,
                       'FEED_URI': 'output.csv',
                       'FEED_FORMAT': 'csv',
                       'DOWNLOAD_DELAY': 1
                       }
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.9",
        "cookie": "summary_id=62ebad3eb685b; _gid=GA1.2.268428139.1659612483; CookieConsent={"
                  "stamp:%27-1%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cver:1"
                  "%2Cutc:1659612483870%2Cregion:%27PK%27}; has_js=1; _ga=GA1.1.1258175118.1659612482; "
                  "__gads=ID=2e6f0693249141d3:T=1659613942:S=ALNI_Madt-bY5O7bT--XOZHFHATb4p3Oiw; "
                  "__gpi=UID=00000a71ffca774b:T=1659613942:RT=1659613942:S=ALNI_Mbdnp_-1WS1e6YdL9GuYXmX7S5T1g; "
                  "_ga_5EMHF6S1M6=GS1.1.1659612482.1.1.1659613976.25; "
                  "_dd_s=logs=1&id=421efaca-c144-44d7-ba50-645d0648088f&created=1659613881357&expire=1659615053885",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"

    }

    def start_requests(self):
        yield Request(url='https://www.psychologytoday.com/au/counselling/nsw/city-of-sydney?page=1',
                      callback=self.parse, headers=self.headers)

    def parse(self, response):
        profile_urls = response.xpath("//a[contains(@class,'profile-title')]/@href").extract()
        for url in profile_urls:
            yield Request(url=url,
                          callback=self.parse_details, headers=self.headers)

        next_page_url = response.xpath(
            "//a[@class='button-element page-btn active-page-btn']/following-sibling::a[1]/@href").get()
        print(next_page_url)
        if next_page_url:
            yield Request(url=next_page_url,
                          callback=self.parse, headers=self.headers)

    def parse_details(self, response):
        name = response.xpath("//div[contains(@class,'profile-title-container')]/h1[@itemprop='name']/text()").get()
        phone_number = response.xpath("//a[@class='phone-number']/text()").get()
        profile_image = response.xpath("//span[@id='profilePhoto']/img/@src").get()
        if not profile_image:
            profile_image = response.xpath("//div[@id='profilePhoto']/img/@src").get()

        url = response.url
        therapist_type_list = []
        therapist_type = response.xpath(
            "//div[@class='spec-list attributes-treatment-orientation']/h5/following-sibling::div/ul/li/span/text()").extract()
        for dt in therapist_type:
            therapist_type_list.append(dt.replace('(', '').replace(')', '').strip())
        therapist_type = ','.join(therapist_type_list)
        try:
            street = response.xpath(
                "//div[contains(@class,'address-mobile')]/div//span[@class='location-wrap']/text()").get().strip()
        except:
            street = ''
        try:
            locality = response.xpath(
                "//div[contains(@class,'address-mobile')]/div//span[@itemprop='addressLocality']/text()").get().strip()
        except:
            locality = ''
        try:
            region = response.xpath(
                "//div[contains(@class,'address-mobile')]/div//span[@itemprop='addressRegion']/text()").get().strip()
        except:
            region = ''
        try:
            code = response.xpath(
                "//div[contains(@class,'address-mobile')]/div//span[@itemprop='postalcode']/text()").get().strip()
        except:
            code = ''

        location = str(street + " " + locality + " " + region + " " + code).replace('\n', '')

        about = ' '.join(response.xpath(
            "//div[@class='profile-statement details-section ']/div[@class='profile-statement-heading']/following-sibling::div/div/div/text()").extract()).strip()
        try:
            pronouns = response.xpath("//div[@id='profHdr']//p[@class='profile-pronouns']/text()").get().strip()
        except:
            pronouns = ''
        spec_list = []
        specialties = response.xpath(
            "//h5[contains(text(),'Specialties')]/following-sibling::div[@class='spec-list attributes-top']/div/ul/li/text()").extract()
        for spec in specialties:
            spec_list.append(spec.strip())
        specialties = ",".join(spec_list)

        issue_list = []
        issues = response.xpath(
            "//h5[contains(text(),'Specialties')]/following-sibling::div[@class='spec-list attributes-issues']/div/ul/li/text()").extract()
        for isu in issues:
            issue_list.append(isu.strip())
        issues = ','.join(issue_list)
        client_focus_list = []
        try:
            ethnicity_one = response.xpath(
                "//h4[contains(text(),'Client Focus')]/following-sibling::div/span[text()='Ethnicity:']/following-sibling::span/text()").get()
        except:
            ethnicity_one = ''

        try:
            ethnicity_two = response.xpath(
                "//h4[contains(text(),'Client Focus')]/following-sibling::div/span[text()='Ethnicity:']/following-sibling::span/following-sibling::text()").get()
        except:
            ethnicity_two = ''
        if ethnicity_one and ethnicity_two:
            ethnicity = ethnicity_one + ethnicity_two
        else:
            ethnicity = ''
        try:
            lang_one = response.xpath(
                "//h4[contains(text(),'Client Focus')]/following-sibling::div/span[text()='I also speak:']/following-sibling::span/text()").get()
        except:
            lang_one = ''

        try:
            lang_two = response.xpath(
                "//h4[contains(text(),'Client Focus')]/following-sibling::div/span[text()='I also speak:']/following-sibling::span/following-sibling::text()").get()
        except:
            lang_two = ''
        if lang_one and lang_two:
            also_speak = lang_one + lang_two
        else:
            also_speak = ''
        try:
            faith = response.xpath(
                "//h4[contains(text(),'Client Focus')]/following-sibling::div/span[text()='Faith:']/following-sibling::span/text()").get().strip()
        except:
            faith = ''

        # client_focus = response.xpath(
        #     "//h4[contains(text(),'Client Focus')]/following-sibling::div/h5[text()='Communities']/following-sibling::div/ul/li/text()").extract()
        # for cf in client_focus:
        #     client_focus_list.append(cf.strip())
        #
        # client_focus = ','.join(client_focus_list)
        client_focus = "Ethnicity: {} ; I also speak: {} ; Faith: {}".format(ethnicity, also_speak, faith)
        age_list = []
        age = response.xpath(
            "//h4[contains(text(),'Client Focus')]/following-sibling::div/h5[text()='Age']/following-sibling::div/ul/li/text()").extract()
        for dt in age:
            age_list.append(dt.strip())
        age = ','.join(age_list)
        modality_list = []
        modalities = response.xpath("//h5[text()='Modality']/following-sibling::div/ul/li/text()").extract()
        for modality in modalities:
            modality_list.append(modality.strip())
        modality = ','.join(modality_list)

        payment_list = []
        payment_node = response.xpath(
            "//h3[contains(text(),'Finances')]/following-sibling::div/div/ul/li")
        for payment in payment_node:
            title = payment.xpath("./strong/text()").get()
            value = payment.xpath("./strong/following-sibling::text()").get()
            if title and value:
                payment_list.append(title.strip() + value.strip())
        finances = ','.join(payment_list)

        qualification_list = []
        qualifications = response.xpath("//h3[text()='Qualifications']/following-sibling::ul/li")
        for qualification in qualifications:
            title = qualification.xpath("./strong/text()").get()
            value = qualification.xpath("./strong/following-sibling::text()").get()
            if title and value:
                qualification_list.append(title.strip() + " " + value.strip())

        qualifications = ','.join(qualification_list)

        edu_list = []
        educations = response.xpath("//h3[text()='Additional Credentials']/following-sibling::ul/li")
        for education in educations:
            title = education.xpath("./strong/text()").get()
            value = education.xpath("./strong/following-sibling::text()").get()
            if title and value:
                edu_list.append(title.strip() + " " + value.strip().replace("\n", '').replace(
                    '                                      ', ''))
        try:
            website = response.xpath("//div[@class='profile-buttons']/a[@data-event-label='website']/@href").get()
        except:
            website = ''
        try:
            offer_online = response.xpath("//a[@id='select-finances-online']/text()").get().strip()
        except:
            offer_online = ''
        Additional_credential = ','.join(edu_list)
        item = dict()
        item['Name'] = name
        item['Phone Number'] = phone_number
        item['Profile Image'] = profile_image
        item['URL'] = url
        item['Therapist Type'] = therapist_type
        item['Location'] = location
        item['About'] = about
        item['Offer_online'] = offer_online
        item['Pronouns'] = pronouns
        item['Specialties'] = specialties
        item['Issues'] = issues
        item['Client Focus'] = client_focus
        item['Age'] = age
        item['Modality'] = modality
        item['Finances'] = finances
        item['Qualifications'] = qualifications
        item['Additional credential'] = Additional_credential
        item['Website'] = website

        yield item
