csvToDspaceSaf
==============

將類似 DSpace 的 CSV 後設資料和附屬的 bitstream 檔案轉換成為 SAF 格式，以便系統管理者使用內建的 SAF 匯入快速大量上傳後設資料和檔案。

A Useful tool to convert csv metadata and bitstream files to SAF format. Lets Administrator can upload metadata and bitstreams with build-in import method.


## CSV Format Description (CSV 格式說明)

本程式採用類似 DSpace 的 CSV 後設資料格式，大略說明如下：

1. CSV 的第一行是後設資料的欄位名稱，採用以下格式 `schema.element.qualifier[langISO]`，如：`dc.contributor.author[zh_TW]
`，如果沒有給定語系，則轉換時也不會指定語系。如果是程式不支援的欄位，將會自動忽略。本程式所用的欄位包含一些例外欄位，列舉如下：
    1. `contents` 欄位：產生 contents 檔案的欄位，不支援檔案政策設定，用來存放跟該後設資料相關的 bitstream 檔名(相對於 CSV 的路徑)。
    1. `handle` 欄位：產生 handle 這個檔案的資料，可用來取代現有 item，如果該欄沒有資料則不會產生。
    1. `id` 欄位：在 DSpace 的 CSV 後設資料格式中是代表 `item_id`，但是在本程式中是所產生之 SAF 資料夾內路徑，可用來產生多階層的 SAF 檔案，如果沒有指定，則程式自動使用流水號產生。
1. 從 CSV 的第二行開始，每一行代表一個 item 的後設資料，如果該欄位有多值，應使用 `||` 分隔，程式將會自動產生多值。如果有需要強制將資料視為單一資料 (不針對 `||` 符號切割)，請於設定檔設定。


## Program Usage (程式使用方法)

待續


## Program Setting (程式設定檔說明)

待續


## Author (程式作者)

TAI, CHUN-MIN `<taichunmin@gmail.com>`

National Chung Hsing University 國立中興大學


## Licence (程式授權)

Please See `LICENSE` file.

請見 `LICENSE` 檔案。
