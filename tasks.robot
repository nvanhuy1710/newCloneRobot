*** Settings ***
Documentation     BKAV Collect Invoice Robot
Library           Collections
Library           OperatingSystem
Library           RPA.Browser.Selenium
Library           DOP.RPA.AgentBridge
Library           DOP.RPA.ProcessArgument
Library           DOP.RPA.Asset
Library           DOP.RPA.Ocr
Library           DOP.RPA.Log
Library           FileUtils
Library           InvoiceOcrUtils
Library           PdfInvoiceUtils
Library           Collections
Library           RPA.PDF
Library           RPA.JSON

*** Variables ***
${FINAL_RESULT}=    ${False}
${SELLER_TAXCODE}=
${INVOICE_TEMPLATE}=
${INVOICE_SERIES}=
${INVOICE_NUMBER}=
${DOWNLOAD_FOLDER}=    ${OUTPUT_DIR}${/}download
${NOT_FOUND_LOOK_UP_CODE}=
${OCR_TYPE}=
${IS_NOT_FOUND_INVOICE}=    ${False}

*** Keywords ***
OCR LookupCode
    [Documentation]    Use OCR Service for looking LookupCode from raw image
    [Arguments]    ${INVOICE_FILE}
    IF    "${OCR_TYPE}" == "AI"
        ${ACESS_TOKEN}=    Get Access Token    vbpo_guest_01    hj-O4eDeKZOb
        ${ACESS_TOKEN}=    Convert String to JSON    ${ACESS_TOKEN}

        ${LOOKUP_CODE}=    Get Lookup Code Ai    ${INVOICE_FILE}    ${ACESS_TOKEN}[access]
        ${LOOKUP_CODE}=    Convert String to JSON    ${LOOKUP_CODE}
        Return From Keyword    ${LOOKUP_CODE}[data][lookup_code]
    ELSE
        ${LOOKUP_CODE}=    Get Lookup Code    ${INVOICE_FILE}
        Return From Keyword    ${LOOKUP_CODE}
    END

*** Keywords ***
Go To Invoice Portal
    Set Download Directory    ${DOWNLOAD_FOLDER}
    Open Chrome Browser    https://van.ehoadon.vn/TCHD    maximized=False

*** Keywords ***
Input Info Invoice
    [Arguments]    ${lookupCode}
    Input Text    id:txtInvoiceCode    ${lookupCode}

*** Keywords ***
Click Button Invoice
    Click Element   id:btnSearch
    ${isNotFoundInvoice}=    Run Keyword And Return Status    Get Text    css:#Bkav_alert_dialog > div > div:nth-child(1) > div:nth-child(2)
    IF    ${isNotFoundInvoice} == ${True}
        Set Global Variable    ${IS_NOT_FOUND_INVOICE}    ${True}
    END
    Select Frame    id:frameViewInvoice
    # Waiting popup
    Wait Until Element Is Visible    id:form1    10s
    # Download XML file
    Click Element    id:btnDownload
    Click Element    id:LinkDownXML
    # Download PDF file
    Click Element    id:btnDownload
    Click Element    id:LinkDownPDF

*** Keywords ***
Wait Download File
    Wait Until Created    ${DOWNLOAD_FOLDER}${/}*.xml    20
    Wait Until Created    ${DOWNLOAD_FOLDER}${/}*.pdf    20

*** Keywords ***
OCR Get Invoice Data
    [Arguments]    ${INVOICE_FILE}
    ${INVOICE_DATA}=    Extract Invoice Data    ${INVOICE_FILE}
    Log Info    Invoice Data: ${INVOICE_DATA}
    [Return]    ${INVOICE_DATA}

*** Tasks ***
Collecting BKAV Invoice Files
    
    Create Directory    ${DOWNLOAD_FOLDER}
    Remove File    ${DOWNLOAD_FOLDER}${/}*.pdf
    Remove File    ${DOWNLOAD_FOLDER}${/}*.xml
    Remove File    ${DOWNLOAD_FOLDER}${/}*.png
    Remove File    ${DOWNLOAD_FOLDER}${/}*.crdownload
    ${INVOICE_FILE}=    Get In Arg    invoiceFile
    ${LOOKUP_CODE}=    Get In Arg    lookupCode
    ${ocrType}=    Get In Arg    ocrType
    Set Global Variable    ${OCR_TYPE}    ${ocrType}[value]
    ${LOOKUP_CODE_IS_AVAILABLE}=    Run keyword And Return Status    Dictionary Should Contain Key    ${LOOKUP_CODE}    value    error=false
    IF    ${LOOKUP_CODE_IS_AVAILABLE} == ${False}
        ${LOOKUP_CODE}=    OCR LookupCode    ${INVOICE_FILE}[value]
    ELSE
        ${LOOKUP_CODE}=    Set Variable    ${LOOKUP_CODE}[value]
    END
    ${isNoneString}=    Check None String    ${LOOKUP_CODE}
    IF    ${isNoneString} == ${True}
        Go To Invoice Portal
        Input Info Invoice    ${LOOKUP_CODE}
        Set Global Variable    ${NOT_FOUND_LOOK_UP_CODE}    ${False}
        Log Info    Found LookupCode: ${LOOKUP_CODE}
        Run Keyword And Ignore Error    Click Button Invoice
        ${waitDownloadFileStatus}=    Run Keyword And Ignore Error    Wait Download File
        IF    "${waitDownloadFileStatus}[0]" == "PASS"
            ${DOWNLOADED_PDF_FILE}=    List Files In Directory    path=${DOWNLOAD_FOLDER}    pattern=*.pdf
            ${DOWNLOADED_PDF_FILE}=    Set Variable    ${DOWNLOAD_FOLDER}${/}${DOWNLOADED_PDF_FILE}[0]
            ${INVOICE_INFO}=    OCR Get Invoice Data    ${DOWNLOADED_PDF_FILE}
            Set Global Variable    ${INVOICE_TEMPLATE}    ${INVOICE_INFO}[invoice_template]
            Set Global Variable    ${INVOICE_SERIES}    ${INVOICE_INFO}[invoice_series]
            Set Global Variable    ${INVOICE_NUMBER}    ${INVOICE_INFO}[invoice_number]
            Set Global Variable    ${SELLER_TAXCODE}    ${INVOICE_INFO}[seller_tax_code]
            Close All Browsers
        END
    ELSE
        Set Global Variable    ${NOT_FOUND_LOOK_UP_CODE}    ${True}
        Log Info    Not found Invoice Lookup Code
    END
    IF    ${IS_NOT_FOUND_INVOICE} == ${False}
        Export Out Arguments
    ELSE
        Log Info    Not found Invoice
    END

*** Keywords ***
Export Out Arguments
    ${RESULT}=    Run keyword And Return Status    File Should Exist    ${DOWNLOAD_FOLDER}${/}*.pdf    error=false
    ${RESULT}=    Run keyword And Return Status    File Should Exist    ${DOWNLOAD_FOLDER}${/}*.xml    error=false
    ${RESULT}=    Run keyword And Return Status    Should Not Be Empty    ${SELLER_TAXCODE}    error=false
    ${RESULT}=    Run keyword And Return Status    Should Not Be Empty    ${INVOICE_SERIES}    error=false
    ${RESULT}=    Run keyword And Return Status    Should Not Be Empty    ${INVOICE_TEMPLATE}    error=false
    ${RESULT}=    Run keyword And Return Status    Should Not Be Empty    ${INVOICE_NUMBER}    error=false
    ${RESULT}=    Run keyword And Return Status    Should Not Be Empty    ${INVOICE_NUMBER}    error=false
    IF    ${RESULT} == ${True}
        # PDF file
        ${DOWNLOADED_PDF_FILE}=    List Files In Directory    path=${DOWNLOAD_FOLDER}    pattern=*.pdf
        Set Out Arg    pdfInvoiceFile    ${DOWNLOAD_FOLDER}${/}${DOWNLOADED_PDF_FILE}[0]
        # XML file
        ${DOWNLOADED_XML_FILE}=    List Files In Directory    path=${DOWNLOAD_FOLDER}    pattern=*.xml
        Set Out Arg    xmlInvoiceFile    ${DOWNLOAD_FOLDER}${/}${DOWNLOADED_XML_FILE}[0]
        # Seller Tax Code
        Set Out Arg    sellerTaxCode    ${SELLER_TAXCODE}
        # Invoie Series
        Set Out Arg    invoiceSeries    ${INVOICE_SERIES}
        # Invoice Template
        Set Out Arg    invoiceTemplate    ${INVOICE_TEMPLATE}
        # Invoice Number
        Set Out Arg    invoiceNumber    ${INVOICE_NUMBER}
        # Final Result
        Set Global Variable    ${FINAL_RESULT}    ${True}
    ELSE
        # Final Result
        Set Global Variable    ${FINAL_RESULT}    ${False}
    END

*** Tasks ***
Set Process Result
    Set Out Arg    result    ${FINAL_RESULT}
