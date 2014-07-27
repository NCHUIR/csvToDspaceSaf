csvToDspaceSaf
==============

將類似 DSpace 的 CSV 後設資料和附屬的 bitstream 檔案轉換成為 SAF 格式，以便系統管理者使用內建的 SAF 匯入快速大量上傳後設資料和檔案。

A Useful tool to convert csv metadata and bitstream files to DSpace SAF format. Lets Administrator can upload metadata and bitstreams with build-in import method.


## CSV Format Description (CSV 格式說明)

本程式採用類似 DSpace 的 CSV 後設資料格式，大略說明如下：

1. CSV 的第一行是後設資料的欄位名稱，採用以下格式 `schema.element.qualifier[langISO]`，如：`dc.contributor.author[zh_TW]`，如果沒有給定語系 `[zh_TW]`，則產生 `dublin_core.xml` 中的 `dcvalue`時也不會指定語系。如果是程式不支援的欄位，將會自動忽略。本程式所用的欄位包含一些例外欄位，列舉如下：
    1. `contents` 欄位：產生 contents 檔案的欄位，不支援檔案政策設定，用來存放跟該後設資料相關的 bitstream 檔名(需相對於 CSV 的路徑)。
    1. `handle` 欄位：產生 handle 這個檔案的資料，可用來取代現有 item，如果該欄沒有資料則不會產生。
    1. `id` 欄位：在 DSpace 的 CSV 後設資料格式中是代表 `item_id`，但是在本程式中是用來產生之 SAF 資料夾內路徑，可用來產生多階層的 SAF 檔案，如果沒有指定，則程式自動使用流水號產生。
1. 從 CSV 的第二行開始，每一行代表一個 item 的後設資料，每一個欄位預設被當作單一值的欄位，如果該欄位有多值，請於設定檔 `setting.json` 的 `multiField` 新增該欄位名稱，則程式將會使用 `dataDelimiter` 來切割欄位。
1. 程式只能接受 `UTF8` 編碼的 CSV 檔案 ( 如果從 Microsoft Excel 轉存的 CSV 格式需先轉換編碼 )

This program can read CSV file format which is very similar to DSpace CSV format. Following are details of the csv format:

1. The first row of csv file is the column name. The column name use following format: `schema.element.qualifier[langISO]`.
 If the column name does not have `[langISO]`, the output `dcvalue` will not specify language. If the column name is not recognized by the program, the column will be ignore. For now, the program only support `dc` schema and following special columns:
    1. `contents` column: generate SAF contents file. You can not specify bitstream's policy. (In fact, the program will not support this feature in the future, you can edit contents file after convert.) The program will consider this field as relative file path to the CSV file path. You can use `dataDelimiter` configured in `setting.json` to separate multiple bitstreams.
    1. `handle` column: generate SAF handle file. If this field is not empty, you can use "replace import" to replace exists item. If the field is empty, the handle file will not generate.
    1. `id` column: In DSpace CSV Format, this column is used to present item_id in DSpace Database, the program use this column to specify where the item should be save in relative to SAF directory. If the field is empty, the program will auto generate a unique directory to save item. (Notice: The program will not validate the directory path.)
1. After the first row of CSV file, the program will consider each "csv row" as metadatas of a item. Each field in row will be treat as single-value field. You can configure `multiField` in `setting.json` to force program use `dataDelimiter` to separate the field data.
1. The program only accept csv file with encoding `UTF-8`, If you use "Microsoft Excel" to save CSV file, you need to convert file encoding first.

## Program Usage (程式使用方法)

`python3 <program-name>.py <csvfile 1 ... n>`

Download python3: <https://www.python.org/downloads/>

您可以在 `Windows` 系統中安裝 `windowsDragHandler.reg` 登錄檔以便您可以直接將 CSV 檔案拖曳到 `csvToDspaceSaf.py` 上來執行。

You can install `windowsDragHandler.reg` and drag csv file to the `csvToDspaceSaf.py` to execute easily in `Windows` system.


## Program Setting (程式設定檔說明)

程式的設定檔位於 `setting.json`，以 `JSON` 格式儲存。在設定檔內的任何設定都會覆蓋掉程式的預設值，您可以在程式內搜尋 `''' Default Settings '''` 來找到程式的預設值。

The setting file of the program is `setting.json`, use `JSON` format.

Any value in the setting.json will overwrite program's default value.

You can search `''' Default Settings '''` in program to find default setting of program.


## Program Requirement (環境需求)

Python 3 以上

Above Python 3


## Author (程式作者)

TAI, CHUN-MIN \<<taichunmin@gmail.com>\>

National Chung Hsing University 國立中興大學


## Licence (程式授權)

請見 `LICENSE` 檔案。

Please See `LICENSE` file.
