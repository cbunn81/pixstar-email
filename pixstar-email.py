import base64
import mimetypes
from pathlib import Path
from urllib.error import HTTPError

import sendgrid
from decouple import config
from sendgrid.helpers.mail import (
    Attachment,
    Content,
    Disposition,
    Email,
    FileContent,
    FileName,
    FileType,
    Mail,
    To,
)


def send_message(subject: str, content: str, attachment: str) -> None:
    """Send the email message using the Sendgrid API. API Key, sender
    address and recipient address are read from env file.
    Args:
        subject (str): Subject line of message
        content (str): Body content of message
        attachment (str): Path to file attachment (only one)
    """
    SENDGRID_API_KEY = config("SENDGRID_API_KEY")
    SENDGRID_SENDER_ADDRESS = config("SENDGRID_SENDER_ADDRESS")
    RECIPIENT_ADDRESS = config("RECIPIENT_ADDRESS")

    message = Mail(
        from_email=Email(SENDGRID_SENDER_ADDRESS),
        to_emails=To(RECIPIENT_ADDRESS),
        subject=subject,
        html_content=Content("text/html", content),
    )

    with open(attachment, "rb") as f:
        data = f.read()
    encoded_file = base64.b64encode(data).decode()

    attachedFile = Attachment(
        FileContent(encoded_file),
        FileName(attachment),
        FileType(mimetypes.guess_type(attachment)[0]),
        Disposition("attachment"),
    )

    message.attachment = attachedFile

    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        response = sg.send(message=message)
        print(response.status_code)
    except HTTPError as e:
        print(e.to_dict)


def get_filelist(paths: list[str], recursive: bool = False) -> list[str]:
    """Get a list of files (but not directories) from a path.
    Args:
        paths (list[str]): The path(s) to search for files.
        recursive (bool, optional): Whether to recursively search the path. Defaults to False.
    Returns:
        list[str]: A list of all filenames, given as absolute paths.
    """
    filelist = []
    for path in paths:
        dir = Path(path)
        if not dir.exists():
            print(f"The directory '{dir}' does not exist.")
        elif not dir.is_dir():
            print(f"'{dir}' is not a directory.")
        else:
            results = dir.rglob("*") if recursive else dir.glob("*")
            filelist.extend([x for x in results if x.is_file()])
    return filelist


def main() -> int:
    paths = ["./videos/"]
    filelist = get_filelist(paths=paths)

    for index, videofile in enumerate(filelist):
        print(f"Sending video {index}: {videofile}")
        subject = f"Video Upload {index}"
        send_message(
            subject=subject,
            content=subject,
            attachment=str(videofile),
        )


if __name__ == "__main__":
    raise SystemExit(main())
