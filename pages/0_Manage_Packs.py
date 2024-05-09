import streamlit as st
import requests

MNEMOPACK_API_URL = "https://api.mnemopack.com"

def load_pack_by_id(pack_id):
    url = f"{MNEMOPACK_API_URL}/packs/{pack_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Assuming the response contains JSON data
    
    print(f"Failed to load pack: {response.status_code} - {response.text}")
    return None

def delete_pack(pack_id, access_key) -> bool:
    url = f"{MNEMOPACK_API_URL}/packs/{pack_id}"
    headers = {'Authorization': f'Bearer {access_key}'}
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        return True
    
    print(f"Failed to delete pack: {response.status_code} - {response.text}")
    return False

def save_pack(pack_id, access_key, type, data):
    pack_data = {
        "data_units": [
            { "type": type, "data": data }
        ]
    }
    
    if pack_id:
        # Update existing pack
        url = f"{MNEMOPACK_API_URL}/packs/{pack_id}"
        headers = {
            "Authorization": f"Bearer {access_key}",
            "Content-Type": "application/json"
        }
        response = requests.put(url, json=pack_data, headers=headers)
        if response.status_code == 200:
            return {'id': pack_id, 'access_key': access_key} 
    else:
        # Create new pack
        url = f"{MNEMOPACK_API_URL}/packs"
        response = requests.post(url, json=pack_data) 
        if response.status_code == 200:
            return response.json() 
    
    if response.status_code in [200, 201]:
        return response.json()  # Assuming the response contains JSON data
    else:
        return f"Failed to save pack: {response.status_code} - {response.text}"

if "pack" in st.session_state:
    pack = st.session_state["pack"]
else:
    pack = None

if "access_key" in st.session_state:
    access_key = st.session_state["access_key"]
else:
    access_key = None

#############################################
## SIDEBAR
st.sidebar.header("Instructions")
st.sidebar.markdown("""
MnemoPack is designed to save data in the cloud. 

**Quick Start**
1. Specify the Pack Type
   1. `text` - textual infromation saved as is
   2. `public_url` - web page is loaded and preprocessed. Special handling for Google Docs and YouTube videos
2. Click the "Save Pack" button. The pack will be created. You will get Pack Id and Access Key generated. Pack Id allows to load the pack in future and talk to it. Access Key allows to update/delete the pack.
                    
Talk with the pack:
1. Use [MnemoPack GPT](https://chatgpt.com/g/g-qjYUTvomW-mnemopack) to talk to the pack

                    
**Example**
1. Specify `mp-fairytale` in the Pack ID and click the "Load Pack" button. You will see the details of the textual pack.
2. Watch the [MnemoPack: Fairy Tale Pack](https://youtu.be/D4XCSNV6-_o?si=auRUfsKmtf3pFR0a) YouTube video to see what you'll get when you talk to the pack. 

[Privace Policy](https://docs.google.com/document/d/e/2PACX-1vTDIondyAvgPSy2bikCT2YEDw0S3FTfdECAbLAXouaYzvA5ig36MhlwW-sVyz6s2okoDr-vfAumjOap/pub)
""")

#############################################
## MAIN AREA
st.title('Manage Packs')
st.text("Create, update, and delete MnemoPacks")

types = ['public_url', 'text']
index = types.index(pack['data_units'][0]['type']) if pack else 0

pack_id = st.text_input("Pack ID:", value=pack['id'] if pack else "")
access_key = st.text_input("Access Key:", value=access_key if access_key else "")

c1, c2, c3, c4 = st.columns([1,1,1,3])
btn_save = c1.button("Save Pack", disabled=False if (pack_id and access_key) or not pack_id else True)
btn_load = c2.button('Load Pack', disabled=False if pack_id else True)
btn_delete = c3.button('Delete Pack', disabled=False if pack_id and access_key else True)
#btn_reset = c4.button('Reset Form')

if btn_load:
    if pack_id:
        pack = load_pack_by_id(pack_id)
        if pack:
            st.session_state["pack"] = pack
            st.rerun()
        else:
            st.error("Failed to load pack")
    else:
        st.error("Pack ID is required to load the pack")

type = st.selectbox('Pack Type:', options = types, index=index)
data = st.text_area("Pack Data:", value=pack['data_units'][0]['data'] if pack else "", height=500)

if btn_save:
    res = save_pack(pack['id'] if pack else None, access_key, type, data)
    if res:
        st.session_state["access_key"] = res['access_key']
        st.session_state["pack"] = load_pack_by_id(res['id'])
        st.rerun()
    else:
        st.error("Failed to save pack")

if btn_delete:
    if not (pack and access_key):
        st.error("Pack needs to be loaded and Access Key specified to delete the pack")
    else:
        delete_pack(pack['id'], access_key)
        del st.session_state["pack"]
        del st.session_state["access_key"]
        st.rerun()

#if btn_reset:
#    del st.session_state["pack"]
#    del st.session_state["access_key"]
#    st.rerun()
