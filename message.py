class Message:
    SUCCESS = "Success."

    AUTHENTICATION_FAILED = "Authentication failed."
    PBX_DOES_NOT_EXIST = "PBX does not exist."
    EXTENSION_LIMIT_HAS_BEEN_REACHED = "Extensions limit has been reached."
    EXTENSION_ALREADY_EXIST = "Extension already exists."
    EXTENSION_DOES_NOT_EXIST = "Extension does not exists."
    PBX_REQUEST_ALREADY_EXIST = "Name is not available because it has been used by other PBX or PBX Request."
    PBX_REQUEST_ALREADY_APPROVED = "PBX Request already approved."
    PBX_REQUEST_DOES_NOT_EXIST = "PBX Request does not exist."
    PBX_REQUEST_NAME_NOT_ACCEPTED = "PBX Request not accepted. Please only use alphanumeric characters."

    EMAIL_NEW_USER_LOGIN_SUBJECT = "Welcome to ViCa!"
    EMAIL_NEW_USER_LOGIN_BODY = "ViCa is Voice Cloud Access provided by CNP Laboratory, Telkom DDS. Please use the service wisely."

    EMAIL_PBX_REQUEST_CREATED_SUBJECT = "ViCa: New PBX Request Notification"
    EMAIL_PBX_REQUEST_CREATED_BODY = "Hi ViCa Admin, there is new PBX Request as follow:\nUser email: {0}\nPBX Request Name: {1}\nPlease go to Admin page to approve or reject it."

    EMAIL_PBX_REQUEST_REJECTED_SUBJECT = "ViCa: PBX Request Rejected"
    EMAIL_PBX_REQUEST_REJECTED_BODY = "We are sorry. Your PBX Request ({0}) is rejected by ViCa Admin."

    EMAIL_PBX_READY_SUBJECT = "ViCa: PBX Ready"
    EMAIL_PBX_READY_BODY = "Congratulations. Your request is approved  on {0} and the PBX ({1}) is ready. It is accessible under IP Address {2}."

    EMAIL_PBX_DELETED_SUBJECT = "ViCa: PBX Deleted"
    EMAIL_PBX_DELETED_BODY = "Your PBX ({0}) has been deleted by ViCa Admin."

    EMAIL_EXTENSION_ADDED_SUBJECT = "ViCa: Extension Notification"
    EMAIL_EXTENSION_ADDED_BODY = "You have been added as an extension owner with the following information.\nPBX Name: {0}\nPBX Address: {1}\nExtension Number: {2}\nExtension Password: {3}\nTo configure your extension, please use a softphone and follow this tutorial:\nhttps://vica.telkomku.com/document/tutorial_softphone.pdf."

    EMAIL_EXTENSION_MODIFIED_SUBJECT = "ViCa: Extension Notification"
    EMAIL_EXTENSION_MODIFIED_BODY = "Your extension is modified. New information is as follow.\nPBX Name: {0}\nPBX Address: {1}\nExtension Number: {2}\nExtension Password: {3}\nTo configure your extension, please use a softphone and follow this tutorial:\nhttps://vica.telkomku.com/document/tutorial_softphone.pdf."

    EMAIL_EXTENSION_DELETED_SUBJECT = "ViCa: Extension Notification"
    EMAIL_EXTENSION_DELETED_BODY = "Your extension has been deleted from PBX: {0}."

