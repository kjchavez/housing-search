#!/usr/bin/env python3
"""Generate docs/data.json for the housing-search tracker site.

Photo URLs point at the original listing CDNs (Zillow / Craigslist) so they
render on GitHub Pages (which does NOT serve Git LFS blobs). The downloaded
copies under candidates/<slug>/photos/ remain the offline archive.

Re-run after editing candidate data:  python3 tools/build_data.py
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Zillow PROPERTY photo hashes (cc_ft gallery crops only; headshots excluded) ---
ZILLOW_PHOTOS = {
 "106-oak-ave-redwood-city":["1ac7be2b62bdc245eff746489ff651ca","4e7c01f329c02a5077a97fdfbdd174d9"],
 "1382-valota-rd-redwood-city":["d82b478a326527558e57d3165b1df4e5","64a2988158869c224744571316e2dbf5","92613460ec0d542df6a26e539be6b1df","8db7d35c64c020cc1a9481f584c5ec89","77ac787f33f5be7d9a9d4844bfa85040"],
 "1-arroyo-view-cir-belmont":["badcfa0f6666f4a26907d5bb843fd643","0c6f6893112ce53c8f1adb09f083da86","235c3f3f2e83af98c74d638ff552b5c0","857601848257d59981f31db4c586ea04","72619c38cd3399203aecbb858a283b1f"],
 "2336-howard-ave-san-carlos":["f15e66f80f60242466cc711d9638a373","78a1b77fe56c1b5e2744270e994d1c9a","20ab0584ff4c1e6570c825c775bead7d","069335efc6d062cc449eb4b239bf2e6c","42b62b9fa3cd257f8a652466314dbd4b"],
 "1405-el-camino-real-144-redwood-city":["8d6749805ce593476a00c07696d45158","35a4ca1964917e19f8ff06d21db0611f","601e6415561976ebcd4b115730ded5ab","c18208e5a86297524fa75155bf78c7ea","b154ddcf76ae084bc277807cdfb59600"],
 "3519-hoover-st-redwood-city":["0790dc11297c46e3678233e4abe3a11f","d5357ab80873a4d3579990753714a6c6","f198be4271a099410fce9d53bf392c87","522f63f52b3629f197144668d44efe61","c2a79293d79b8a72f811b52f04d30663"],
 "763-college-ave-menlo-park":["e74fc6082db8f4295bbbb44bc914e506","331bf1d33a126db0ea30c58dc8a6eaf4","b1c67dffb56976fc67bcd2a117acaf43","62d5a547ab5733e09b690f189d28233a","1bd95e6dfe26d23dbf5bf22aea597481"],
 "1009-s-norfolk-st-san-mateo":["625c630eab5409c94eeec2ddbd01f629","75bf2e199c0f467d9360c24c40aafa66","6ddcf7d59fc60727352e15c7d837ed9b","244bd814c4624b90720d03fc04b7cfe3","50f4f11839a2e2ff74d4916976ec1780"],
}

def zphotos(slug):
    hs = ZILLOW_PHOTOS.get(slug, [])
    return [{"thumb": f"https://photos.zillowstatic.com/fp/{h}-cc_ft_576.jpg",
             "full":  f"https://photos.zillowstatic.com/fp/{h}-cc_ft_1536.jpg"} for h in hs]

# --- Craigslist image base IDs per slug ---
CL_PHOTOS = {
 "cl-rwc-modern-farm-orchard":"00y0y_jLJ8DQcEKin_0CI0t2 00000_5yhk4I1yU3X_0CI0t2 00O0O_klwljZQuoLf_0CI0t2 00V0V_1l6Zy032bUf_0x30oN 00P0P_32GZqMisXLf_0x20oM 00u0u_6CySBsleQtu_0CI0t2 01313_89b16CePiMo_0CI0t2",
 "cl-rwc-201-yarborough":"00g0g_3TTZSO8DUSs_0gw0aW 00s0s_dZTuTbp6Rrh_0gw0aW 01414_4oZZp3zTBhb_0gw0aT 00808_48Et4jjqFVI_0gw0aW 00505_4rpyrtXq3ew_0gw0aV 00u0u_5aCNmBgyvRN_0gw0aU 00x0x_hAKugxke0H5_0gw0aW",
 "cl-menlo-remodeled-yards":"01111_7KCTb8qpKHu_08S06F 01414_eKxQsgxmSeM_0gw0co 00y0y_3Giy8KJzd8a_0cI08k 00V0V_3HAwi8JisJ3_0ak06T 00c0c_97D9JtTH1AO_09i0co 00x0x_bBnxURLkcMP_0cI08h 00A0A_bhgO8GXk5Fj_0cI08k",
 "cl-sancarlos-2bed-bonus":"00202_eV3hGUGZYHN_0nm0hw 00g0g_eh9yqQNbJUW_0gl0t2 00e0e_b5jpzj9Xg6R_0gw0b1 00E0E_cwNjWAfSZww_08g0co 01717_cRSdyfVYVYJ_0gw0b3 00A0A_7jQb8hRmebL_0gw0b1 00404_gIHvwnFyKPa_0gw0b1",
 "cl-belmont-modern-3d":"00U0U_2orcTjUffYG_0gK0d6 01212_6dvlTh7FjhL_0fm09J 00f0f_ajr49dHEuf4_0fl09L 00707_ipbBqtsiIVp_0fs09J 00p0p_c8DzBvpHMr8_0fr09I",
 "cl-menlo-detached-adu-pets":"00h0h_4ph8ZP0n8Qu_0gw0oM 01010_8u0PrtfsAIK_0CI0re 01414_9TfRrZIAmxL_0tu0h2 00Q0Q_802Uloh6Fuy_08K0c2",
 "cl-atherton-guest-house":"00B0B_4GCRnKOkagY_0CI0t2 00L0L_6ajkMlqAJy5_0CI0t2 01010_eIRUwzXbCjf_0CI0t2 00404_50YAz2aFbQo_0CI0t2 01515_auEiyKCdbZR_0CI0t2 00C0C_gzagwjUXyqt_0CI0lM 00V0V_iOAIqvhIi2e_0t20CI",
}
def cphotos(slug):
    return [{"thumb": f"https://images.craigslist.org/{b}_600x450.jpg",
             "full":  f"https://images.craigslist.org/{b}_1200x900.jpg"} for b in CL_PHOTOS.get(slug,"").split()]

# match levels: yes / partial / no / unknown
C = lambda beds,busy,light,yard,dist,ceil,rent,gar,house: {
    "beds":beds,"busy":busy,"light":light,"yard":yard,"dist":dist,
    "ceilings":ceil,"rent":rent,"garage":gar,"house":house}

# slug: (name, city, rent, rentLabel, beds, baths, sqft, type, avail, petsLabel, petsOk,
#        garageLabel, yardLabel, distMi, bikeMin, score, tier, status, srcName, srcUrl, summary, flags, criteria)
DATA = [
 ("106-oak-ave-redwood-city","106 Oak Ave","Redwood City",5500,"$5,500",4,2,1700,"House","Now",
  "Cats, dogs OK",True,"Attached garage","Yard — verify fence",1.2,7,8.5,"1","to-contact",
  "Zillow","https://www.zillow.com/homedetails/106-Oak-Ave-Redwood-City-CA-94061/15565827_zpid/",
  "Newly renovated 4bd/2ba house, attached garage, dogs OK — and the closest of all (7-min bike to Veterans Blvd). Verify the backyard is fenced.",
  ["Verify fenced yard"], C("yes","partial","yes","unknown","yes","unknown","yes","yes","yes")),

 ("cl-belmont-modern-3d","Belmont “Modern 3D” Home","Belmont",6000,"$6,000",3,2,1690,"House","Jun 15",
  "Small dogs OK",True,"2-car attached","Deck + yard — verify fence",5,28,8.5,"1","to-contact",
  "Craigslist","https://sfbay.craigslist.org/pen/apa/d/belmont-beautiful-modern-belmont-3d/7937152559.html",
  "Stunning open-concept home: high ceilings, Viking kitchen, canyon views, 2-car garage, small dogs OK. Only knock is Belmont distance (~5mi, hilly).",
  ["Verify yard fencing","~5mi hilly bike"], C("yes","yes","yes","partial","partial","yes","yes","partial","yes")),

 ("1382-valota-rd-redwood-city","1382 Valota Rd","Redwood City",3650,"$3,650",2,1,880,"House (duplex unit)","Now",
  "Dogs OK (case-by-case)",True,"1-car carport","Private fenced yard",2,12,7.5,"1","to-contact",
  "Zillow","https://www.zillow.com/homedetails/1382-Valota-Rd-Redwood-City-CA-94061/462945854_zpid/",
  "Best value: private fenced yard, dogs OK, bright open-concept, quiet near Woodside Plaza, just $3,650. Carport (not enclosed garage); 880 sqft.",
  ["Carport not garage","Confirm dog approval"], C("yes","yes","yes","yes","yes","unknown","yes","partial","yes")),

 ("1740-whipple-ave-redwood-city","1740 Whipple Ave (1928 Tudor)","Redwood City",6950,"$6,950",3,1,1450,"House","Jun 15",
  "Pet friendly",True,"1-car garage","Private yard + spa",1.5,9,7.0,"1","new",
  "Rent.com","https://www.rent.com/r/1740-whipple-ave-redwood-city-ca-lv3092857397",
  "Charming 1928 Tudor on a rare 9,700 sqft lot: refinished hardwood, sunroom, private backyard w/ pergola + jacuzzi, pet-friendly. Pricey ($6,950), 1 bath, 1-car garage.",
  ["$6,950 top of stretch","Only 1 bath"], C("yes","partial","yes","yes","yes","partial","partial","partial","yes")),

 ("1-arroyo-view-cir-belmont","1 Arroyo View Cir","Belmont",5500,"$5,500",3,2,1420,"House (HOA)","Now — apps in",
  "Cats / small dogs OK (2)",True,"Attached garage","Verify (HOA community)",4.5,25,7.0,"1","to-contact",
  "Zillow","https://www.zillow.com/homedetails/1-Arroyo-View-Cir-Belmont-CA-94002/15547056_zpid/",
  "Active rental in a Belmont HOA community: 3bd, attached garage, small dogs OK. They're already reviewing applications — move fast. Likely no private fenced yard.",
  ["Already taking applications","Verify private yard"], C("yes","yes","unknown","partial","partial","unknown","yes","yes","yes")),

 ("cl-rwc-201-yarborough","201 Yarborough Ln","Redwood City",6200,"$6,200",4,3,2147,"House (gated)","Jul 7",
  "Verify",None,"Attached garage","Verify",3,16,7.0,"1","to-contact",
  "Craigslist","https://sfbay.craigslist.org/pen/apa/d/redwood-city-beauty-bedrooms-bathrooms/7938593380.html",
  "Spacious 4bd/3ba in a gated community, attached garage, $6,200. Two open questions could make it #1: pets allowed? private fenced yard?",
  ["Verify pets","Verify fenced yard"], C("yes","yes","partial","unknown","partial","unknown","yes","yes","yes")),

 ("cl-menlo-remodeled-yards","788 18th Ave","Menlo Park",4750,"$4,750",2,2,1090,"House","Jun 15",
  "No pets (except service animal)",False,"Finished 2-car garage","Landscaped backyard",3.5,18,5.0,"2","new",
  "Craigslist","https://sfbay.craigslist.org/pen/apa/d/menlo-park-beautifully-remodeled-home/7938986458.html",
  "Beautiful remodel with the ideal gym garage (finished 2-car) at a great price — but NO PETS. Would be ~8.5 if they'd make a dog exception. Worth a call.",
  ["No pets — ask for exception"], C("yes","yes","partial","yes","partial","unknown","yes","yes","yes")),

 ("cl-sancarlos-2bed-bonus","San Carlos 2BR + bonus","San Carlos",5800,"$5,800",2,1,1210,"House","Aug 25",
  "No pets",False,"1-car attached","Huge fenced yard",3.5,18,5.5,"2","new",
  "Craigslist","https://sfbay.craigslist.org/pen/apa/d/san-carlos-perfect-location-beautifully/7935730013.html",
  "Remodeled house with the best fenced yard of the batch (terraced garden + treehouse) — but NO PETS and not available until Aug 25.",
  ["No pets","Available Aug 25 (late)"], C("yes","yes","partial","yes","partial","unknown","yes","partial","yes")),

 ("cl-rwc-house-lease-jul1","Upper RWC 2BR (lease 7/1)","Redwood City",5000,"$5,000",2,2,1250,"House","Jul 1",
  "Verify",None,"No garage (driveway)","Front + back yards",3,16,6.0,"2","new",
  "Craigslist","https://sfbay.craigslist.org/pen/apa/d/redwood-city-house-for-lease/7934426468.html",
  "Quiet upper-RWC house with a bay-view deck and yards, in budget — but explicitly NO garage (kills the gym requirement). No photos in the post.",
  ["No garage","No photos posted"], C("yes","yes","partial","partial","partial","unknown","yes","no","yes")),

 ("cl-rwc-modern-farm-orchard","RWC Modern Farm/Orchard","Redwood City",7000,"$7,000",2,1,1000,"House (furnished)","Jul 18",
  "Dogs ≤20lb OK",True,"No garage (street)","Patios + orchard",2.5,12,6.0,"2","new",
  "Craigslist","https://sfbay.craigslist.org/pen/apa/d/redwood-city-new-gorgeous-modern-home/7939164840.html",
  "Gorgeous 2021 cottage: cathedral ceilings, tons of light, dog-tolerant, ~2.5mi to Veterans — but furnished/short-term-oriented, no garage, top-of-budget $7K.",
  ["Furnished / short-term","No garage","20lb dog limit"], C("yes","yes","yes","partial","yes","yes","partial","no","yes")),

 ("1405-el-camino-real-144-redwood-city","1405 El Camino Real #144 (Highwater)","Redwood City",5570,"$5,570",2,1,996,"Apartment","Verify",
  "Cats, dogs OK",True,"Shared building garage","None (apartment)",0.4,3,5.0,"2","new",
  "Zillow","https://www.zillow.com/homedetails/1405-El-Camino-Real-144-Redwood-City-CA-94063/2054336778_zpid/",
  "Upscale 2021 LEED-Gold apartment, dog-friendly, the most walkable (~0.4mi to Veterans Blvd) — but a busy-street apartment with no private yard or garage.",
  ["Apartment, not house","Busy street","No yard/private garage"], C("yes","no","partial","no","yes","partial","yes","no","no")),

 ("3519-hoover-st-redwood-city","3519 Hoover St","Redwood City",3995,"$3,995",2,1,950,"House (duplex front)","Jun 8",
  "No pets",False,"No garage (driveway)","Front yard porch",1.5,9,5.0,"2","new",
  "Zillow","https://www.zillow.com/homedetails/3519-Hoover-St-Redwood-City-CA-94063/15568349_zpid/",
  "Fully remodeled cheap RWC house close to Veterans Blvd — but NO pets and NO garage. (Earlier 'for sale $1.8M' info was wrong; it's a $3,995 rental.)",
  ["No pets","No garage"], C("yes","yes","partial","partial","yes","unknown","yes","no","yes")),

 ("cl-menlo-detached-adu-pets","Menlo Park detached ADU","Menlo Park",4200,"$4,200",1,1,450,"ADU / cottage","Jul 1",
  "Pets OK",True,"Carport","Private garden — verify fence",3.5,18,5.0,"3","new",
  "Craigslist","https://sfbay.craigslist.org/pen/apa/d/menlo-park-modern-detached-adu-in-menlo/7933675759.html",
  "Brand-new pet-friendly standalone cottage, well priced — but a 1bd/450sqft with no garage. Good fallback if you don't need the garage.",
  ["1 bedroom","No garage"], C("no","yes","partial","partial","partial","unknown","yes","no","partial")),

 ("2336-howard-ave-san-carlos","2336 Howard Ave","San Carlos",5500,"$5,500",2,2,1000,"House","Verify",
  "No pets",False,"Verify","Landscaped",3,16,4.5,"3","new",
  "Zillow","https://www.zillow.com/homedetails/2336-Howard-Ave-San-Carlos-CA-94070/15560170_zpid/",
  "Pleasant San Carlos house in budget, <1mi to downtown — but NO pets and parking/garage unspecified.",
  ["No pets","Garage unconfirmed"], C("yes","yes","partial","partial","partial","unknown","yes","unknown","yes")),

 ("cl-atherton-guest-house","Atherton guest house (furnished)","Atherton",4100,"$4,100",2,1,650,"Guest house","Jul 1",
  "No pets",False,"No garage (driveway)","Garden patio",4,20,4.0,"3","new",
  "Craigslist","https://sfbay.craigslist.org/pen/apa/d/atherton-furnished-2br-1ba-guest-house/7936652769.html",
  "Furnished cottage on a quiet Atherton estate at a fair all-in price — but small (650sqft), no pets, no garage.",
  ["No pets","No garage","Small / furnished"], C("yes","yes","partial","partial","partial","unknown","yes","no","partial")),

 ("763-college-ave-menlo-park","763 College Ave","Menlo Park",6500,"$6,500",3,2,1620,"House + studio","Jul 1",
  "Cats / small dogs OK",True,"Detached parking","Large lot — verify fence",3.7,20,4.0,"3","new",
  "Zillow","https://www.zillow.com/homedetails/763-College-Ave-Menlo-Park-CA-94025/15596432_zpid/",
  "Lovely, light, dog-OK home in Allied Arts — but it's a 2–3 month SHORT-TERM sublet, so it doesn't fit a permanent move.",
  ["Short-term 2–3 months only"], C("yes","yes","yes","partial","partial","unknown","partial","no","yes")),

 ("1009-s-norfolk-st-san-mateo","1009 S Norfolk St","San Mateo",2650,"$2,650",1,1,500,"In-law unit","Verify",
  "No pets",False,"Street parking","None",7,45,2.0,"3","new",
  "Zillow","https://www.zillow.com/homedetails/1009-S-Norfolk-St-San-Mateo-CA-94401/15525824_zpid/",
  "Cheap and bright, but a junior 1bd in-law unit, no pets, no garage/yard, and ~7mi from Veterans Blvd.",
  ["1 bedroom","No pets","~7mi away"], C("no","partial","yes","no","no","unknown","yes","no","no")),

 ("307-santa-clara-ave-redwood-city","307 Santa Clara Ave","Redwood City",6500,"~$6,500",3,2,1950,"House","Not available",
  "No pets",False,"3-car garage","Fantastic backyard",2,12,3.0,"x","passed",
  "Zumper","https://www.zumper.com/address/307-santa-clara-ave-redwood-city-ca-94061-usa",
  "Great house on paper (3-car garage, big backyard, studio suite) — but it's a notify-me (not currently available) and NO pets.",
  ["Not currently available","No pets"], C("yes","partial","partial","partial","yes","unknown","partial","yes","yes")),

 ("427-clinton-st-redwood-city","427 Clinton St","Redwood City",None,"Off market",3,3,1463,"House","Off market",
  "—",None,"~290 sqft garage","6,500 sqft lot",1.5,9,2.0,"x","passed",
  "Zillow","https://www.zillow.com/homedetails/427-Clinton-St-Redwood-City-CA-94062/15564200_zpid/",
  "Off market — not a rental. The earlier ~$5,700 figure was a Rent Zestimate. Watch item only if it ever lists.",
  ["Off market — not for rent"], C("yes","partial","unknown","partial","yes","unknown","unknown","partial","yes")),
]

PHOTO_FALLBACK = {  # slugs whose photos come from craigslist or none
}

out = []
for row in DATA:
    (slug,name,city,rent,rentLabel,beds,baths,sqft,typ,avail,petsLabel,petsOk,
     garageLabel,yardLabel,distMi,bikeMin,score,tier,status,srcName,srcUrl,summary,flags,crit) = row
    if slug in ZILLOW_PHOTOS: photos = zphotos(slug)
    elif slug in CL_PHOTOS:  photos = cphotos(slug)
    else:                    photos = []
    out.append({
        "slug":slug,"name":name,"city":city,"rent":rent,"rentLabel":rentLabel,
        "beds":beds,"baths":baths,"sqft":sqft,"type":typ,"avail":avail,
        "pets":petsLabel,"petsOk":petsOk,"garage":garageLabel,"yard":yardLabel,
        "distMi":distMi,"bikeMin":bikeMin,"score":score,"tier":tier,
        "defaultStatus":status,"source":{"name":srcName,"url":srcUrl},
        "summary":summary,"flags":flags,"criteria":crit,"photos":photos,
        "folder":f"candidates/{slug}/",
    })

docs = os.path.join(ROOT,"docs")
os.makedirs(docs, exist_ok=True)
meta = {"updated":"2026-06-07","anchor":"1155 Veterans Blvd, Redwood City","count":len(out)}
json.dump({"meta":meta,"candidates":out}, open(os.path.join(docs,"data.json"),"w"), indent=1)
print(f"wrote docs/data.json — {len(out)} candidates, "
      f"{sum(len(c['photos']) for c in out)} photo URLs")
