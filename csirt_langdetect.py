from langdetect import detect

def detect_language(input_text):
    try:
        language_code = detect(input_text)
        return language_code
    except:
        return None

# # Example usage:
# # text_to_detect = 'リモートの Windows ホストにインストールされている Microsoft Edge のバージョンは、108.0.1462.54 より前です。したがって、2022 年 12 月 16 日のアドバイザリに記載されている複数の脆弱性の影響を受けます。'
# text_to_detect = """
# 件名: 緊急：リモートの Windows ホストにおける Microsoft Edge の脆弱性 (CVE-2022-4436 から CVE-2022-4440)

# 差出人: 山田太郎
# メールアドレス: yamada.taro123@emailprovider.com
# 電話番号: +81 (0)12-3456-7890

# 拝啓、ITチームの皆様

# お世話になっております。山田太郎と申します。ITセキュリティ部門を代表して、リモートのWindowsホストとMicrosoft Edgeにおける重要な問題について連絡いたします。

# 私どもの確認によりますと、リモートのホストにインストールされているMicrosoft Edgeのバージョンが108.0.1462.54より古いものとなっております。そのため、2022年12月16日のアドバイザリに記載されている複数の脆弱性の影響を受ける可能性があるとのことです。

# 以下に、脆弱性とそのシステムへの影響について詳細を記載いたします：

# CVE-2022-4436 (Chromiumセキュリティ深刻度: 高)

# 脆弱性内容：Google ChromeのBlink Mediaにおけるメモリ解放後のUse After Free。
# 潜在的なリスク：リモート攻撃者が細工されたHTMLページを介してヒープ破損を悪用する可能性があります。
# CVE-2022-4437 (Chromiumセキュリティ深刻度: 高)

# 脆弱性内容：Google ChromeのMojo IPCにおけるメモリ解放後のUse After Free。
# 潜在的なリスク：リモート攻撃者が細工されたHTMLページを介してヒープ破損を悪用する可能性があります。
# CVE-2022-4438 (Chromiumセキュリティ深刻度: 高)

# 脆弱性内容：Google ChromeのBlink Framesにおけるメモリ解放後のUse After Free。
# 潜在的なリスク：リモート攻撃者がユーザーに特定のUI操作を行わせ、細工したHTMLページを経由してヒープ破壊を悪用する可能性があります。
# CVE-2022-4439 (Chromiumセキュリティ深刻度: 高)

# 脆弱性内容：Chrome OS上のGoogle ChromeのAuraにおけるメモリ解放後のUse After Free。
# 潜在的なリスク：リモート攻撃者が特定のUI操作を行うようユーザーを騙し、特定のUI操作を介してヒープ破壊を悪用する可能性があります。
# CVE-2022-4440 (Chromiumセキュリティ深刻度: 中)

# 脆弱性内容：Google ChromeのProfilesにおけるメモリ解放後のUse After Free。
# 潜在的なリスク：リモート攻撃者が細工されたHTMLページを介してヒープ破損を悪用する可能性があります。
# Nessusはこれらの問題をテストしておらず、代わりにアプリケーションの自己報告されたバージョン番号にのみ依存しています。

# システムのセキュリティと機密性を確保するために、緊急の対応をお願いいたします。Microsoft Edgeをセキュリティパッチが適用された最新バージョンに更新していただくことが重要です。これにより、潜在的なリモート攻撃からネットワークを保護し、重要なデータを守ることができます。

# ご不明点やお手伝いが必要な場合は、どうぞお気軽にお問い合わせください。

# お手数をおかけいたしますが、ご対応をお願いいたします。

# 敬具、

# 山田太郎
# ITセキュリティ部門
# """
# detected_language = detect_language(text_to_detect)
# if detected_language:
#     print(f"Detected language: {detected_language}")
# else:
#     print("Language detection failed.")
