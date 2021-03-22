def create_header_block(header) -> dict:
    return {"type": "header",
            "text": {"type": "plain_text",
                     "text": header,
                     "emoji": True}
            }


def get_sev_icon(severity) -> str:
    return {
        "high": "https://i.imgur.com/7h75Aox.png",
        "medium": "https://i.imgur.com/MtPw8GH.png",
        "low": "https://i.imgur.com/4ZJPTpS.png"
    }[severity]


def create_mrkdn_block(string) -> dict:
    return {"type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{string}"
            }
            }


def create_vul_section(vul, org_details, conn_dict) -> dict:
    lib = vul['library']
    elements = [{"type": "image",
                 "image_url": get_sev_icon(vul['severity']),
                 "alt_text": "Severity"
                 },
                {
                    "type": "mrkdwn",
                    "text": f"<{conn_dict['wss_url']}/Wss/WSS.html#!securityVulnerability;id={vul['name']};orgToken={org_details['orgToken']}|{vul['name']}> - "
                            f"<{conn_dict['wss_url']}/Wss/WSS.html#!libraryDetails;uuid={lib['keyUuid']};orgToken={org_details['orgToken']}|{lib['filename']}>\n"
                            f"*Product:* {vul['product']} *Project:* {vul['project']} *Score:* {vul['score']}"
                    # TODO CONVERT PROD/PROJ to URLs?
                }
                ]

    return {"type": "context",
            "elements": elements}


def create_lib_vul_section(lib) -> dict:  # TODO: CONTINUE WORKING ON MESSAGE
    elements = [{"type": "mrkdwn",
                 "text": f"<{lib['lib_url']}|{lib['filename']}> "
                         f"{print_set(lib['vulnerabilities'])}"
                 }]

    return {"type": "context",
            "elements": elements}


def create_lib_vul_block(header_text, libs) -> list:
    block = [create_header_block(header_text),
             create_mrkdn_block(f"Found {len(libs)} libs with vulnerabilities")
             ]
    for lib in libs:
        block.append(create_lib_vul_section(lib))
        # block.append({"type": "divider"})

    return block


def print_set(set_to_p) -> str:
    max_e_per_set = 3
    ret = []
    if len(set_to_p) < max_e_per_set:
        ret = ', '.join(set_to_p)
    else:
        for i, val in enumerate(set_to_p):
            if i < max_e_per_set:
                ret.append(val)
            else:
                break
        ret = ', '.join(ret) + " ..."

    return ret
