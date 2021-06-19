import imageio
import numpy as np
import os
import concurrent.futures
import matplotlib


def analyze_image(image_path):
    astropi = imageio.imread(image_path)
    masque_rouge = astropi[:, :, 0] > 130
    masque_vert = astropi[:, :, 1] > 130
    masque_bleu = astropi[:, :, 2] > 130
    masque_ocean_rouge = np.logical_and(astropi[:, :, 0]> 5, astropi[:, :, 0] <85)
    masque_ocean_vert = np.logical_and(astropi[:, :, 1]> 20, astropi[:, :, 1] <85)
    masque_ocean_bleu = np.logical_and(astropi[:, :, 2]> 20, astropi[:, :, 2] <85)

    masque_terre_rouge = np.logical_and(astropi[:, :, 0]>85, astropi[:, :, 0] <130)
    masque_terre_vert = np.logical_and(astropi[:, :, 1]> 85, astropi[:, :, 1] <130)
    masque_terre_bleu = np.logical_and(astropi[:, :, 2]> 85, astropi[:, :, 2] <130)
    masque_final_sky = np.logical_and(masque_rouge, masque_vert, masque_bleu)
    masque_final_sea = np.logical_and(masque_ocean_rouge, masque_ocean_vert, masque_ocean_bleu)
    # peut etre a utiliser masque_final_foret = np.logical_and(masque_foret_rouge, masque_foret_vert, masque_foret_bleu)
    masque_final_terre = np.logical_and(masque_terre_rouge, masque_terre_vert, masque_terre_bleu)
    astropi[masque_final_terre] = [0, 255, 0]
    astropi[masque_final_sea] = [0, 0, 255]
    astropi[masque_final_sky] = [255, 0, 0]
    total = astropi.shape[0] * astropi.shape[1]
    percentage_sea = (np.sum(masque_final_sea)/total)*100
    percentage_sky = (np.sum(masque_final_sky)/total)*100
    percentage_terre = (np.sum(masque_final_terre)/total)*100
    return (image_path,astropi, masque_final_sea, masque_final_terre, masque_final_sky, percentage_sea, percentage_terre, percentage_sky)


def main():
    all_files = os.listdir()
    all_images = []
    processes = []
    result_images = []

    for file in all_files:
        extension = os.path.splitext(file)
        if extension[1] == ".jpg":
            all_images.append(file)
    print(all_images)
    print(len(all_images))
    with concurrent.futures.ProcessPoolExecutor() as executor:

        for i in range(0, len(all_images)-1,os.cpu_count()):
            if (len(all_images)-i) - os.cpu_count() < os.cpu_count():
                for j in range(i, len(all_images)):
                    f1 = executor.submit(analyze_image,all_images[j])
                    processes.append(f1)
                for u in processes:
                    result_images.append(u.result())
                    print(f"got result for secondary {result_images[len(result_images)-1][0]}")
                processes = []
                break
            for y in range(i,i+os.cpu_count()):
                print(y)
                f1 = executor.submit(analyze_image,all_images[y])
                processes.append(f1)
            for u in processes:
                result_images.append(u.result())
                print(f"got result for {result_images[len(result_images)-1][0]}")
            processes = []
    #print(result_images)
    print(len(result_images))
    print(len(all_images))
    sky_per=0
    terre_per=0
    sea_per=0
    for i in range(len(result_images)):
        sky_per+=result_images[i][7]
        terre_per+=result_images[i][6]
        sea_per+=result_images[i][5]
    try:
        sky_per = sky_per/len(result_images)
    except :
        sky_per = 0
    try:
        terre_per=terre_per/len(result_images)
    except :
        terre_per = 0
    try:
        sea_per=sea_per/len(result_images)
    except :
        sea_per = 0
    print(sky_per,terre_per,sea_per)
    #os.mkdir("treated_images")
    albedo = sea_per*0.10+terre_per*0.25+sky_per*0.70
    albedo = (albedo/100)*1.30
    print(albedo)
    """
    for i in result_images[1]:
        print(i)
        #imageio.imwrite("treated_images",i)
    """
    
    """
    for u in range(len(result_images)):
        imageio.imsave(f"treated_images/image{u}.png", result_images[u][1])
    """
    """
    matplotlib.pyplot.imshow(result_images[10][2])
    matplotlib.pyplot.imshow(result_images[10][3])
    matplotlib.pyplot.imshow(result_images[10][4])
    matplotlib.pyplot.imshow(result_images[16][1])
    """

if __name__ == '__main__':

    main()
