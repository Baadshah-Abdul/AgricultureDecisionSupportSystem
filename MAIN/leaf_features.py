# ============================================================
# leaf_features.py - Feature Extraction for Leaf Images
# ============================================================

import cv2
import numpy as np
import os

# ============================================================
# COLOR FEATURES
# ============================================================

def extract_color_features(img_rgb):
    """
    Extract improved color-based features from the image.
    """
    features = {}
    
    img_float = img_rgb.astype(float)
    
    R = img_float[:, :, 0]
    G = img_float[:, :, 1]
    B = img_float[:, :, 2]
    
    total_pixels = R.size
    
    # Feature 1: Mean Green Intensity
    features['mean_green'] = np.mean(G)
    
    # Feature 2: Yellow Percentage
    yellow_mask = (R > 120) & (G > 120) & (B < 90) & (R > B + 30) & (G > B + 30)
    features['yellow_percentage'] = (np.sum(yellow_mask) / total_pixels) * 100
    
    # Feature 3: Mean Red Intensity
    features['mean_red'] = np.mean(R)
    
    # Feature 4: Purple Tint Score
    purple_mask = (R > G + 10) & (R > B)
    if np.sum(purple_mask) > 0:
        features['purple_tint'] = np.mean((R[purple_mask] - G[purple_mask]) / (R[purple_mask] + G[purple_mask] + 1)) * 100
    else:
        features['purple_tint'] = 0
    
    # Feature 5: Brown Percentage
    brown_mask = (R > 70) & (R < 160) & (G > 40) & (G < 110) & (B > 10) & (B < 70) & (R > G) & (G > B)
    features['brown_percentage'] = (np.sum(brown_mask) / total_pixels) * 100
    
    # Feature 6: Green-to-Yellow Ratio
    green_mask = (G > R) & (G > B) & (G > 100)
    green_pixels = np.sum(green_mask)
    yellow_pixels = np.sum(yellow_mask)
    features['green_yellow_ratio'] = green_pixels / (yellow_pixels + 1)
    
    # Feature 7: Color Variance
    features['color_variance'] = np.std(G)
    
    # Feature 8: Red-to-Green Ratio
    features['red_green_ratio'] = np.mean(R) / (np.mean(G) + 1)
    
    # Feature 9: Yellow Uniformity
    if yellow_pixels > 0:
        yellow_R = R[yellow_mask]
        yellow_G = G[yellow_mask]
        features['yellow_uniformity'] = 1.0 / (np.std(yellow_R) + np.std(yellow_G) + 1)
    else:
        features['yellow_uniformity'] = 0
    
    return features


# ============================================================
# REGION DETECTION
# ============================================================

def get_leaf_regions(img_rgb):
    """
    Find actual leaf tip, base, and margins using contours.
    """
    h, w = img_rgb.shape[:2]
    
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    
    leaf_contour = max(contours, key=cv2.contourArea)
    
    topmost = tuple(leaf_contour[leaf_contour[:, :, 1].argmin()][0])
    bottommost = tuple(leaf_contour[leaf_contour[:, :, 1].argmax()][0])
    leftmost = tuple(leaf_contour[leaf_contour[:, :, 0].argmin()][0])
    rightmost = tuple(leaf_contour[leaf_contour[:, :, 0].argmax()][0])
    
    tip_y = topmost[1]
    base_y = bottommost[1]
    left_x = leftmost[0]
    right_x = rightmost[0]
    
    tip_height = int((base_y - tip_y) * 0.15)
    margin_width = int((right_x - left_x) * 0.08)
    
    regions = {
        'tip_region': (tip_y, tip_y + tip_height, left_x, right_x),
        'base_region': (base_y - tip_height, base_y, left_x, right_x),
        'left_margin': (tip_y, base_y, left_x, left_x + margin_width),
        'right_margin': (tip_y, base_y, right_x - margin_width, right_x),
        'center_region': (tip_y + tip_height, base_y - tip_height, 
                          left_x + margin_width, right_x - margin_width)
    }
    
    return regions


# ============================================================
# IMPROVED SPATIAL FEATURES
# ============================================================

def extract_tip_yellowing_improved(img_rgb):
    """
    Measure yellow specifically in the actual leaf tip.
    """
    regions = get_leaf_regions(img_rgb)
    if regions is None:
        return {'tip_yellowing': 0}
    
    tip_y1, tip_y2, tip_x1, tip_x2 = regions['tip_region']
    tip_region = img_rgb[tip_y1:tip_y2, tip_x1:tip_x2]
    
    R = tip_region[:, :, 0].astype(float)
    G = tip_region[:, :, 1].astype(float)
    B = tip_region[:, :, 2].astype(float)
    
    yellow_mask = (R > 120) & (G > 120) & (B < 90) & (R > B + 30) & (G > B + 30)
    
    total_pixels = R.size
    yellow_pixels = np.sum(yellow_mask)
    
    return {'tip_yellowing': yellow_pixels / total_pixels if total_pixels > 0 else 0}


def extract_margin_browning_improved(img_rgb):
    """
    Measure brown specifically along actual leaf margins.
    """
    regions = get_leaf_regions(img_rgb)
    if regions is None:
        return {'margin_browning': 0}
    
    l_y1, l_y2, l_x1, l_x2 = regions['left_margin']
    r_y1, r_y2, r_x1, r_x2 = regions['right_margin']
    
    left_margin = img_rgb[l_y1:l_y2, l_x1:l_x2]
    right_margin = img_rgb[r_y1:r_y2, r_x1:r_x2]
    
    def brown_percentage(region):
        if region.size == 0:
            return 0
        R = region[:, :, 0].astype(float)
        G = region[:, :, 1].astype(float)
        B = region[:, :, 2].astype(float)
        brown_mask = (R > 70) & (R < 160) & (G > 40) & (G < 110) & (B > 10) & (B < 70) & (R > G) & (G > B)
        return np.sum(brown_mask) / region.size
    
    left_brown = brown_percentage(left_margin)
    right_brown = brown_percentage(right_margin)
    
    return {'margin_browning': (left_brown + right_brown) / 2}


def extract_basal_green(img_rgb):
    """
    Measure green retained at leaf base.
    """
    regions = get_leaf_regions(img_rgb)
    if regions is None:
        return {'basal_green': 0}
    
    base_y1, base_y2, base_x1, base_x2 = regions['base_region']
    base_region = img_rgb[base_y1:base_y2, base_x1:base_x2]
    
    R = base_region[:, :, 0].astype(float)
    G = base_region[:, :, 1].astype(float)
    B = base_region[:, :, 2].astype(float)
    
    green_mask = (G > R) & (G > B) & (G > 100)
    
    total_pixels = R.size
    green_pixels = np.sum(green_mask)
    
    return {'basal_green': green_pixels / total_pixels if total_pixels > 0 else 0}


def extract_v_shape_gradient(img_rgb):
    """
    Measure yellow gradient from tip to middle.
    """
    features = {}
    tip_yellow = extract_tip_yellowing_improved(img_rgb).get('tip_yellowing', 0)
    
    regions = get_leaf_regions(img_rgb)
    if regions is None:
        return {'v_shape_gradient': 0}
    
    c_y1, c_y2, c_x1, c_x2 = regions['center_region']
    center_region = img_rgb[c_y1:c_y2, c_x1:c_x2]
    
    R = center_region[:, :, 0].astype(float)
    G = center_region[:, :, 1].astype(float)
    B = center_region[:, :, 2].astype(float)
    
    yellow_mask = (R > 120) & (G > 120) & (B < 90) & (R > B + 30) & (G > B + 30)
    
    total_pixels = R.size
    yellow_pixels = np.sum(yellow_mask)
    center_yellow = yellow_pixels / total_pixels if total_pixels > 0 else 0
    
    return {'v_shape_gradient': tip_yellow - center_yellow}


# ============================================================
# TEXTURE AND SHAPE FEATURES
# ============================================================

def extract_texture_shape_features(img_rgb):
    """
    Extract texture and basic shape features.
    """
    features = {}
    
    img_float = img_rgb.astype(float)
    G = img_float[:, :, 1]
    R = img_float[:, :, 0]
    
    # Feature: Smoothness
    features['smoothness'] = 1.0 / (np.std(G) + 1)
    
    # Feature: Texture Contrast
    features['texture_contrast'] = np.std(R) + np.std(G)
    
    # Feature: Spot Density
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    spots = [c for c in contours if 10 < cv2.contourArea(c) < 500]
    features['spot_count'] = len(spots)
    features['spot_density'] = features['spot_count'] / (R.size / 10000)
    
    # Feature: Width-to-Length Ratio and Leaf Area
    all_contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if all_contours:
        largest = max(all_contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        features['width_length_ratio'] = w / h if h > 0 else 0
        features['leaf_area'] = cv2.contourArea(largest)
    else:
        features['width_length_ratio'] = 0
        features['leaf_area'] = 0
    
    # Feature: Edge Roughness
    if all_contours and len(largest) > 0:
        perimeter = cv2.arcLength(largest, True)
        area = cv2.contourArea(largest)
        if area > 0:
            features['edge_roughness'] = (perimeter * perimeter) / (4 * np.pi * area)
        else:
            features['edge_roughness'] = 0
    else:
        features['edge_roughness'] = 0
    
    return features


# ============================================================
# MASTER FEATURE EXTRACTOR
# ============================================================

def extract_all_features_improved(image_path):
    """
    Extract all features with improved region detection.
    """
    img = cv2.imread(image_path)
    if img is None:
        return None
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    features = {}
    
    # Color features
    features.update(extract_color_features(img_rgb))
    
    # Spatial features
    features.update(extract_tip_yellowing_improved(img_rgb))
    features.update(extract_margin_browning_improved(img_rgb))
    features.update(extract_basal_green(img_rgb))
    features.update(extract_v_shape_gradient(img_rgb))
    
    # Texture/shape features
    features.update(extract_texture_shape_features(img_rgb))
    
    # Calculate tip_base_yellow_ratio
    tip_yellow = features.get('tip_yellowing', 0)
    base_yellow = 0.001  # Avoid division by zero
    if 'basal_green' in features:
        base_yellow = 1.0 - features['basal_green']
    features['tip_base_yellow_ratio'] = tip_yellow / base_yellow if base_yellow > 0 else 0
    
    return features


# ============================================================
# BATCH EXTRACTION
# ============================================================

def extract_from_folder(folder_path, label, limit=None):
    """
    Extract features from all images in a folder.
    """
    data = []
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if limit:
        files = files[:limit]
    
    for f in files:
        features = extract_all_features_improved(os.path.join(folder_path, f))
        if features:
            features['label'] = label
            features['filename'] = f
            data.append(features)
    
    return data