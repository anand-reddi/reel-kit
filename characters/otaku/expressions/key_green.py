import cv2, numpy as np, sys, os
A='/mnt/user-data/attachments/c134f771-b774-5086-a650-2d5eaa9ea4fa/'
files=['b19bc01a','a6cb613c','51bb89cf','43871792','ff28cb95','3f45bff9','0f8462d5','472d33f3','6461c8c3','302bc4d7','aeffc9d3','193f165c','b478e9da','425cd0c7','0514f1b6','0664c1d9']
names=['celebrate','unimpressed','listen','calm_smile','phone_shock','surprised','thinking','evil_grin','cringe','laugh','side_eye','thumbs_wink','point_you','smirk','mind_blown','point_up']
OUT='/root/reelkit/characters/otaku/expressions/'
for k,(f,n) in enumerate(zip(files,names)):
    im=cv2.imread(A+f+'-image.png'); h,w=im.shape[:2]
    # 1) remove the generator's sparkle mark in the bottom-right corner (inpaint)
    m=np.zeros((h,w),np.uint8); cv2.circle(m,(int(w*.945),int(h*.958)),int(w*.032),255,-1)
    im=cv2.inpaint(im,m,7,cv2.INPAINT_TELEA)
    im=cv2.inpaint(im,m,15,cv2.INPAINT_TELEA)
    # 2) chroma key: how much greener than red/blue
    f32=im.astype(np.float32); B,G,Rr=f32[...,0],f32[...,1],f32[...,2]
    d=G-np.maximum(Rr,B)
    a=1-np.clip((d-25)/(70-25),0,1)          # d>=70 fully green bg, <=25 fully subject
    n_,lab,stt,_=cv2.connectedComponentsWithStats((a>0.5).astype(np.uint8),8)
    keep=np.zeros_like(a,np.uint8)
    for j in range(1,n_):
        if stt[j,cv2.CC_STAT_AREA]>0.002*h*w: keep[lab==j]=1
    keep=cv2.morphologyEx(keep,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
    holes=cv2.floodFill(keep.copy()*255,None,(0,0),128)[1]; keep[holes==0]=1     # fill enclosed holes
    a=a*cv2.dilate(keep,np.ones((5,5),np.uint8)).astype(np.float32)
    a=cv2.GaussianBlur(a,(3,3),0)
    # 3) despill: no pixel may be greener than its red/blue
    G2=np.minimum(G,np.maximum(Rr,B)*1.02); f32[...,1]=G2
    rgba=np.dstack([f32[...,2],f32[...,1],f32[...,0],a*255]).clip(0,255).astype(np.uint8)
    from PIL import Image
    p=Image.fromarray(rgba,'RGBA'); bb=p.split()[3].point(lambda v:255 if v>20 else 0).getbbox()
    p.resize((1100,1100),Image.LANCZOS).save(OUT+f'{k+1:02d}_{n}.png'); print(k+1,n,bb)
