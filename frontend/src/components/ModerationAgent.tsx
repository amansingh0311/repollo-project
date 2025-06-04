import { useState, useEffect, useCallback } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Loader2,
  Shield,
  AlertTriangle,
  Upload,
  Image as ImageIcon,
  X,
  Eye,
  Plus,
  Trash2,
} from 'lucide-react';
import { ModerationResults } from './ModerationResults';
import { BatchModerationResults } from './BatchModerationResults';
import {
  ModerationResponse,
  BatchModerationResponse,
  ImageUpload,
} from '@/types/agents';

export function ModerationAgent() {
  const [moderationText, setModerationText] = useState('');
  const [moderationImageUrls, setModerationImageUrls] = useState<string[]>([
    '',
  ]);
  const [moderationImageFiles, setModerationImageFiles] = useState<
    ImageUpload[]
  >([]);
  const [moderationMethod, setModerationMethod] = useState<'upload' | 'url'>(
    'upload'
  );
  const [strictMode, setStrictMode] = useState(false);
  const [moderationLoading, setModerationLoading] = useState(false);
  const [moderationResponse, setModerationResponse] =
    useState<ModerationResponse | null>(null);
  const [batchModerationResponse, setBatchModerationResponse] =
    useState<BatchModerationResponse | null>(null);
  const [moderationError, setModerationError] = useState<string | null>(null);

  // Cleanup function for preview URLs
  useEffect(() => {
    return () => {
      moderationImageFiles.forEach((img) => {
        if (img.preview) {
          URL.revokeObjectURL(img.preview);
        }
      });
    };
  }, [moderationImageFiles]);

  const convertFileToBase64 = useCallback((file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        if (typeof reader.result === 'string') {
          // Remove data:image/type;base64, prefix
          const base64 = reader.result.split(',')[1];
          resolve(base64);
        } else {
          reject(new Error('Failed to convert file to base64'));
        }
      };
      reader.onerror = (error) => reject(error);
    });
  }, []);

  const handleImageFileChange = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(event.target.files || []);
      if (files.length === 0) return;

      const allowedTypes = [
        'image/png',
        'image/jpeg',
        'image/jpg',
        'image/webp',
        'image/gif',
      ];
      const maxSize = 50 * 1024 * 1024; // 50MB in bytes

      const newImageUploads: ImageUpload[] = [];
      let hasError = false;

      for (const file of files) {
        // Validate file type
        if (!allowedTypes.includes(file.type)) {
          setModerationError(
            'Please upload valid image files (PNG, JPEG, WEBP, GIF)'
          );
          hasError = true;
          break;
        }

        // Validate file size
        if (file.size > maxSize) {
          setModerationError(`File "${file.name}" exceeds the 50MB size limit`);
          hasError = true;
          break;
        }

        // Create preview
        const previewUrl = URL.createObjectURL(file);
        newImageUploads.push({
          file,
          preview: previewUrl,
          id: `${Date.now()}-${Math.random()}`,
        });
      }

      if (!hasError) {
        setModerationImageFiles((prev) => [...prev, ...newImageUploads]);
        setModerationError(null);
      } else {
        // Cleanup any created preview URLs on error
        newImageUploads.forEach((img) => URL.revokeObjectURL(img.preview));
      }

      // Reset input
      event.target.value = '';
    },
    []
  );

  const removeImageFile = useCallback((id: string) => {
    setModerationImageFiles((prev) => {
      const updated = prev.filter((img) => img.id !== id);
      // Cleanup the removed preview URL
      const removed = prev.find((img) => img.id === id);
      if (removed?.preview) {
        URL.revokeObjectURL(removed.preview);
      }
      return updated;
    });
  }, []);

  const handleImageUrlChange = useCallback((index: number, url: string) => {
    setModerationImageUrls((prev) => {
      const updated = [...prev];
      updated[index] = url;
      return updated;
    });
  }, []);

  const addImageUrl = useCallback(() => {
    setModerationImageUrls((prev) => [...prev, '']);
  }, []);

  const removeImageUrl = useCallback((index: number) => {
    setModerationImageUrls((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const switchModerationMethod = useCallback(
    (method: 'upload' | 'url') => {
      setModerationMethod(method);

      // Clear the other method's state
      if (method === 'upload') {
        setModerationImageUrls(['']);
      } else {
        // Clear image files and their preview URLs
        moderationImageFiles.forEach((img) => {
          if (img.preview) {
            URL.revokeObjectURL(img.preview);
          }
        });
        setModerationImageFiles([]);
      }
      setModerationError(null);
    },
    [moderationImageFiles]
  );

  const handleModerationAnalysis = async () => {
    const hasText = moderationText.trim();
    const hasImageFiles = moderationImageFiles.length > 0;
    const hasImageUrls = moderationImageUrls.some((url) => url.trim());

    if (!hasText && !hasImageFiles && !hasImageUrls) {
      setModerationError(
        'Please provide text content, upload images, or enter image URLs'
      );
      return;
    }

    setModerationLoading(true);
    setModerationError(null);
    setModerationResponse(null);
    setBatchModerationResponse(null);

    try {
      const items: any[] = [];

      // Add text content if provided
      if (hasText) {
        items.push({
          text: moderationText.trim(),
          strict_mode: strictMode,
        });
      }

      // Add image files
      if (hasImageFiles) {
        for (const imageUpload of moderationImageFiles) {
          try {
            const base64Data = await convertFileToBase64(imageUpload.file);
            items.push({
              image_base64: base64Data,
              image_filename: imageUpload.file.name,
              strict_mode: strictMode,
            });
          } catch (err) {
            throw new Error(
              `Failed to process image file: ${imageUpload.file.name}`
            );
          }
        }
      }

      // Add image URLs
      if (hasImageUrls) {
        const validUrls = moderationImageUrls.filter((url) => url.trim());
        for (const url of validUrls) {
          items.push({
            image_url: url.trim(),
            strict_mode: strictMode,
          });
        }
      }

      // Determine if we need batch processing
      const isBatch = items.length > 1;

      if (isBatch) {
        // Use batch API
        const response = await fetch('/api/moderation/batch-analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            items,
            strict_mode: strictMode,
            parallel_processing: true,
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail ||
              data.error ||
              'Failed to process batch moderation analysis'
          );
        }

        setBatchModerationResponse(data);
      } else {
        // Use single item API
        const response = await fetch('/api/moderation/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(items[0]),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail || data.error || 'Failed to process moderation analysis'
          );
        }

        setModerationResponse(data);
      }
    } catch (err) {
      setModerationError(
        err instanceof Error ? err.message : 'Unknown error occurred'
      );
    } finally {
      setModerationLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Shield className="h-5 w-5 text-green-500" />
          <span>Content Moderation Analysis</span>
        </CardTitle>
        <CardDescription>
          Analyze text and/or image content for safety, policy violations, and
          harmful content detection. Supports batch processing for multiple
          items.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Text Content */}
        <div className="space-y-2">
          <label htmlFor="moderation-text" className="text-sm font-medium">
            Text Content (Optional)
          </label>
          <Textarea
            id="moderation-text"
            placeholder="Enter text content to analyze for safety and policy violations..."
            value={moderationText}
            onChange={(e) => setModerationText(e.target.value)}
            className="min-h-[100px]"
          />
        </div>

        {/* Image Content */}
        <div className="space-y-4">
          <Label className="text-sm font-medium">
            Image Content (Optional)
          </Label>

          {/* Image Upload Options */}
          <Tabs
            value={moderationMethod}
            onValueChange={(value) =>
              switchModerationMethod(value as 'upload' | 'url')
            }
            className="w-full"
          >
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="upload">Upload Images</TabsTrigger>
              <TabsTrigger value="url">Image URLs</TabsTrigger>
            </TabsList>

            <TabsContent value="upload" className="space-y-3">
              <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-gray-400 dark:hover:border-gray-500 transition-colors">
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/jpg,image/webp,image/gif"
                  onChange={handleImageFileChange}
                  className="hidden"
                  id="image-upload"
                  multiple
                />
                <label htmlFor="image-upload" className="cursor-pointer">
                  <Upload className="h-10 w-10 mx-auto mb-3 text-gray-400" />
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500">
                    PNG, JPEG, WEBP, GIF up to 50MB each. Multiple files
                    supported.
                  </p>
                </label>
              </div>

              {/* Uploaded Images Preview */}
              {moderationImageFiles.length > 0 && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">
                      {moderationImageFiles.length} image(s) selected:
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {moderationImageFiles.map((imageUpload) => (
                      <div
                        key={imageUpload.id}
                        className="relative border rounded-lg overflow-hidden"
                      >
                        <img
                          src={imageUpload.preview}
                          alt={imageUpload.file.name}
                          className="w-full h-32 object-cover"
                        />
                        <Button
                          size="sm"
                          variant="destructive"
                          className="absolute top-2 right-2"
                          onClick={() => removeImageFile(imageUpload.id)}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                        <div className="p-2 bg-white dark:bg-slate-800">
                          <div className="flex items-center space-x-2">
                            <ImageIcon className="h-3 w-3" />
                            <span className="text-xs truncate">
                              {imageUpload.file.name}
                            </span>
                          </div>
                          <span className="text-xs text-muted-foreground">
                            {(imageUpload.file.size / 1024 / 1024).toFixed(2)}{' '}
                            MB
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </TabsContent>

            <TabsContent value="url" className="space-y-3">
              {moderationImageUrls.map((url, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <Input
                    placeholder={`https://example.com/image${index + 1}.jpg`}
                    value={url}
                    onChange={(e) =>
                      handleImageUrlChange(index, e.target.value)
                    }
                    className="flex-1"
                  />
                  {moderationImageUrls.length > 1 && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => removeImageUrl(index)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}

              <Button
                size="sm"
                variant="outline"
                onClick={addImageUrl}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Another URL
              </Button>

              {/* URL Preview */}
              {moderationImageUrls.some((url) => url.trim()) && (
                <div className="space-y-3">
                  <span className="text-sm font-medium">Image Preview(s):</span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {moderationImageUrls
                      .filter((url) => url.trim())
                      .map((url, index) => (
                        <div
                          key={index}
                          className="relative border rounded-lg overflow-hidden"
                        >
                          <img
                            src={url}
                            alt={`URL Image ${index + 1}`}
                            className="w-full h-32 object-cover"
                            onError={(e) => {
                              const target = e.target as HTMLImageElement;
                              target.style.display = 'none';
                            }}
                          />
                          <div className="p-2 bg-white dark:bg-slate-800">
                            <div className="flex items-center space-x-2">
                              <Eye className="h-3 w-3" />
                              <span className="text-xs truncate">
                                URL {index + 1}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>

        {/* Strict Mode Toggle */}
        <div className="flex items-center space-x-2">
          <Switch
            id="strict-mode"
            checked={strictMode}
            onCheckedChange={setStrictMode}
          />
          <Label htmlFor="strict-mode" className="text-sm">
            Strict Mode (Enhanced sensitivity)
          </Label>
        </div>

        <Button
          onClick={handleModerationAnalysis}
          disabled={
            moderationLoading ||
            (!moderationText.trim() &&
              moderationImageFiles.length === 0 &&
              !moderationImageUrls.some((url) => url.trim()))
          }
          className="w-full"
        >
          {moderationLoading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Analyzing Content...
            </>
          ) : (
            <>
              <Shield className="h-4 w-4 mr-2" />
              Analyze Content
            </>
          )}
        </Button>

        {moderationError && (
          <Alert className="border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="text-red-800 dark:text-red-200">
              {moderationError}
            </AlertDescription>
          </Alert>
        )}

        {/* Results */}
        {moderationResponse && (
          <ModerationResults response={moderationResponse} />
        )}
        {batchModerationResponse && (
          <BatchModerationResults response={batchModerationResponse} />
        )}
      </CardContent>
    </Card>
  );
}
