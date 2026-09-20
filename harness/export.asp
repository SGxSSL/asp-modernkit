<%@ Language=VBScript %>
<% Option Explicit %>
<%
Response.ContentType = "application/json"
Response.Expires = -1
Response.AddHeader "Pragma", "no-cache"
Response.AddHeader "Cache-Control", "no-store, no-cache, must-revalidate"

' Helper function to escape JSON strings
Function EscapeJson(ByVal str)
    If IsNull(str) Then
        EscapeJson = "null"
        Exit Function
    End If
    Dim s : s = CStr(str)
    s = Replace(s, "\", "\\")
    s = Replace(s, """", "\""")
    s = Replace(s, vbCr, "\r")
    s = Replace(s, vbLf, "\n")
    s = Replace(s, vbTab, "\t")
    EscapeJson = """" & s & """"
End Function

Dim conn, rs, schemaRs
Dim dbPath, connString
Dim tableName
Dim firstTable, firstRow, firstCol
Dim fld

' Path to the database - using Server.MapPath assuming it's dropped in /public
dbPath = Server.MapPath("../data/development.mdb")
connString = "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" & dbPath

Set conn = Server.CreateObject("ADODB.Connection")
conn.Open connString

' Get tables
Set schemaRs = conn.OpenSchema(20) ' 20 = adSchemaTables

Response.Write "{"
Response.Write """tables"": ["

firstTable = True
Do Until schemaRs.EOF
    tableName = schemaRs("TABLE_NAME")
    
    ' Ignore system tables
    If schemaRs("TABLE_TYPE") = "TABLE" And Left(tableName, 4) <> "MSys" Then
        If Not firstTable Then Response.Write ","
        firstTable = False
        
        Response.Write "{"
        Response.Write """name"": " & EscapeJson(tableName) & ","
        
        ' Open table to get columns and data
        Set rs = Server.CreateObject("ADODB.Recordset")
        rs.Open "SELECT * FROM [" & tableName & "]", conn, 0, 1 ' adOpenForwardOnly, adLockReadOnly
        
        ' Write columns
        Response.Write """columns"": ["
        firstCol = True
        For Each fld In rs.Fields
            If Not firstCol Then Response.Write ","
            firstCol = False
            Response.Write "{"
            Response.Write """name"": " & EscapeJson(fld.Name) & ","
            Response.Write """type"": " & fld.Type
            Response.Write "}"
        Next
        Response.Write "],"
        
        ' Write rows
        Response.Write """rows"": ["
        firstRow = True
        Do Until rs.EOF
            If Not firstRow Then Response.Write ","
            firstRow = False
            
            Response.Write "{"
            firstCol = True
            For Each fld In rs.Fields
                If Not firstCol Then Response.Write ","
                firstCol = False
                
                Response.Write """" & fld.Name & """: "
                
                If IsNull(fld.Value) Then
                    Response.Write "null"
                ElseIf fld.Type = 11 Or fld.Type = 2 Then ' Boolean or Integer
                    ' VBScript boolean to lowercase string for JSON
                    If VarType(fld.Value) = vbBoolean Then
                        If fld.Value Then Response.Write "true" Else Response.Write "false"
                    Else
                        ' Numbers
                        Dim val : val = fld.Value
                        If IsNumeric(val) Then
                            ' ensure decimal separator is dot, not comma based on locale, though VBScript uses locale
                            Response.Write Replace(CStr(val), ",", ".")
                        Else
                            Response.Write EscapeJson(val)
                        End If
                    End If
                Else
                    Response.Write EscapeJson(fld.Value)
                End If
            Next
            Response.Write "}"
            
            rs.MoveNext
        Loop
        Response.Write "]"
        
        rs.Close
        Set rs = Nothing
        
        Response.Write "}"
    End If
    schemaRs.MoveNext
Loop

Response.Write "]"
Response.Write "}"

schemaRs.Close
Set schemaRs = Nothing
conn.Close
Set conn = Nothing
%>
