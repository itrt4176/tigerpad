With CreateObject("WScript.Shell")

    ' Pass 0 as the second parameter to hide the window...
    .Run "cmd /c run_relay.bat > logs\relay.log", 0, True

End With