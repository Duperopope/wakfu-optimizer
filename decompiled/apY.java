/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  GC
 *  apX
 *  apZ
 *  aqa
 *  aqb
 *  aqc
 *  aqd
 *  aqg
 *  aqi
 *  aql
 *  aqt
 *  gnu.trove.iterator.TIntObjectIterator
 *  gnu.trove.map.hash.TIntObjectHashMap
 *  gnu.trove.map.hash.TLongObjectHashMap
 *  gnu.trove.procedure.TIntObjectProcedure
 *  org.apache.commons.pool.ObjectPool
 */
import gnu.trove.iterator.TIntObjectIterator;
import gnu.trove.map.hash.TIntObjectHashMap;
import gnu.trove.map.hash.TLongObjectHashMap;
import gnu.trove.procedure.TIntObjectProcedure;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.EOFException;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FilenameFilter;
import java.io.FilterInputStream;
import java.io.FilterOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.lang.reflect.Field;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.commons.pool.ObjectPool;

public final class apY
extends apS {
    private final TIntObjectHashMap<ArrayList<aqc>> cPJ = new TIntObjectHashMap();
    private final TIntObjectHashMap<TIntObjectHashMap<ArrayList<aqi>>> cPK = new TIntObjectHashMap();
    private static final boolean cPL = false;
    final String cPM;
    private final int cPN = 20000000;
    private final int cPO = 500;
    private aqc cPP;
    private final Object cPQ = new Object();
    final StringBuilder cPR = new StringBuilder(20);
    private static final Pattern cPS = Pattern.compile("[^a-zA-Z0-9-_/\\.]");
    private boolean cPz;
    private final File cPT;
    private final File cPU;
    private final File cPV;
    private final File cPW;
    private final TLongObjectHashMap<File> cPX = new TLongObjectHashMap();
    final TIntObjectHashMap<File> cPY = new TIntObjectHashMap();
    private static final String cPZ = "data.";
    private static final String cQa = ".bdat";
    private static final String cQb = "index.";
    private static final String cQc = ".bdat";
    private static final String cQd = "metadata.bdat";
    private final aqt cQe;
    private final aqt cQf = aqt.b((ObjectPool)aqt.cQF);
    private final aqt cQg = aqt.b((ObjectPool)aqt.cQF);

    protected apY(String string) {
        this(string, false);
    }

    private apY(String string, boolean bl) {
        this.cPM = apY.fG(string);
        this.cPW = new File(this.cPM);
        this.cPT = new File(this.cPM + "~building_index.tmp");
        this.cPU = new File(this.cPM + "~building_data.tmp");
        this.cPV = new File(this.cPM + cQd);
        this.setName("BinaryStorage (" + this.cPM + ")");
        aqt aqt2 = this.cQe = bl ? aqt.b((ObjectPool)aqt.cQG) : aqt.b((ObjectPool)aqt.cQF);
        if (this.bGb()) {
            this.start();
        } else {
            cPe.error("Echec de l'initialisation du binary storage " + String.valueOf(this));
        }
    }

    public static boolean fF(String string) {
        File file = new File(apY.fG(string) + cQd);
        return file.exists();
    }

    private static String fG(String string) {
        Object object = string;
        if (((String)(object = cPS.matcher((CharSequence)object).replaceAll("_"))).charAt(0) == '/') {
            object = ((String)object).substring(1, ((String)object).length());
        }
        if (((String)object).charAt(((String)object).length() - 1) != '/') {
            object = (String)object + "/";
        }
        return object;
    }

    public boolean blc() {
        return this.cPz;
    }

    @Override
    protected String bGc() {
        return this.cPM;
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    @Override
    protected boolean bGb() {
        Object object = this.cPQ;
        synchronized (object) {
            block29: {
                if (this.cPz) {
                    cPe.error("Binary storage already initialize : " + this.cPM);
                    return false;
                }
                try {
                    if (this.cPW.exists() && !this.cPW.isDirectory()) {
                        cPe.error("Tentative de changement de workspace [" + this.cPM + "] vers un fichier [not directory] existant [Aborted & Shutdown]");
                        return false;
                    }
                    if (!this.cPW.exists() && !this.cPW.mkdirs()) {
                        cPe.error("Impossible de creer l'arborescence de repertoire [" + this.cPM + "] lors d'un changement de workspace inexistant [Aborted & Shutdown]");
                        return false;
                    }
                    this.cPJ.clear();
                    if (!this.cPV.exists()) {
                        this.cPV.createNewFile();
                        cPe.info("Fichier de meta donn\u00e9es non trouv\u00e9 pour le chargement de la source binaire : Creation d'une nouvelle source");
                        break block29;
                    }
                    Object object2 = null;
                    FilterInputStream filterInputStream = null;
                    try {
                        object2 = new FileInputStream(this.cPV);
                        filterInputStream = this.cQg.b((FileInputStream)object2);
                        try {
                            while (true) {
                                int n = ((DataInputStream)filterInputStream).readInt();
                                int n2 = ((DataInputStream)filterInputStream).readInt();
                                int n3 = ((DataInputStream)filterInputStream).readInt();
                                int n4 = ((DataInputStream)filterInputStream).readInt();
                                int n5 = n;
                                ArrayList<aqc> arrayList = (ArrayList<aqc>)this.cPJ.get(n5);
                                if (arrayList == null) {
                                    arrayList = new ArrayList<aqc>();
                                    this.cPJ.put(n5, arrayList);
                                }
                                arrayList.add(new aqc(this, n5, n2, n3, n4));
                            }
                        }
                        catch (EOFException eOFException) {
                            if (filterInputStream != null) {
                                try {
                                    filterInputStream.close();
                                }
                                catch (IOException iOException) {
                                    cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                                }
                            }
                            if (object2 != null) {
                                try {
                                    ((FileInputStream)object2).close();
                                }
                                catch (IOException iOException) {
                                    cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                                }
                            }
                        }
                    }
                    catch (Throwable throwable) {
                        if (filterInputStream != null) {
                            try {
                                filterInputStream.close();
                            }
                            catch (IOException iOException) {
                                cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                            }
                        }
                        if (object2 != null) {
                            try {
                                ((FileInputStream)object2).close();
                            }
                            catch (IOException iOException) {
                                cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                            }
                        }
                        throw throwable;
                    }
                }
                catch (FileNotFoundException fileNotFoundException) {
                    cPe.error(fileNotFoundException.getMessage(), (Throwable)fileNotFoundException);
                    return false;
                }
                catch (IOException iOException) {
                    cPe.error(iOException.getMessage(), (Throwable)iOException);
                    return false;
                }
            }
            this.cPz = true;
            for (FilterInputStream filterInputStream : this.cPf) {
                filterInputStream.a(this, this.bGc());
            }
            return true;
        }
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    private void bGo() {
        try {
            FileOutputStream fileOutputStream = null;
            FilterOutputStream filterOutputStream = null;
            try {
                fileOutputStream = new FileOutputStream(this.cPV, false);
                FilterOutputStream filterOutputStream2 = filterOutputStream = this.cQg.b((OutputStream)fileOutputStream);
                if (!this.cPJ.isEmpty()) {
                    this.cPJ.forEachEntry((TIntObjectProcedure)new apZ(this, (DataOutputStream)filterOutputStream2));
                }
            }
            finally {
                if (filterOutputStream != null) {
                    try {
                        filterOutputStream.close();
                    }
                    catch (IOException iOException) {
                        cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                    }
                }
                if (fileOutputStream != null) {
                    try {
                        fileOutputStream.close();
                    }
                    catch (IOException iOException) {
                        cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                    }
                }
            }
        }
        catch (FileNotFoundException fileNotFoundException) {
            cPe.error(fileNotFoundException.getMessage(), (Throwable)fileNotFoundException);
        }
        catch (IOException iOException) {
            cPe.error(iOException.getMessage(), (Throwable)iOException);
        }
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    @Override
    protected void c(apX apX2) {
        Object object = this.cPQ;
        synchronized (object) {
            ArrayList<aqi> arrayList = this.a(cPl, apX2.aFS(), (Object)apX2.bGh(), 1);
            if (arrayList.size() <= 0) {
                this.d(apX2);
            } else {
                this.a(apX2, arrayList.get(0));
            }
        }
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    private void d(apX apX2) {
        byte[] byArray = apX2.aFR();
        if (byArray == null) {
            cPe.error("Tentative de sauvegarde d'un binary storable qui n'a aucun bloc de donn\u00e9es " + String.valueOf(apX2));
            return;
        }
        long l = apX2.dy(byArray);
        int n = byArray.length + 4 + 2 + 4;
        this.bT(apX2.aFS(), n);
        try {
            Field[] fieldArray;
            long l2;
            File file = this.cPP.cQl;
            if (!file.exists()) {
                file.createNewFile();
            }
            FileOutputStream fileOutputStream = null;
            FilterOutputStream filterOutputStream = null;
            try {
                fileOutputStream = new FileOutputStream(this.cPP.cQl, true);
                filterOutputStream = this.cQe.b((OutputStream)fileOutputStream);
                l2 = fileOutputStream.getChannel().size();
                fieldArray = new aqg(apX2.bGh(), apX2.bGi(), byArray);
                fieldArray.f((DataOutputStream)filterOutputStream);
            }
            finally {
                if (filterOutputStream != null) {
                    try {
                        filterOutputStream.close();
                    }
                    catch (IOException iOException) {
                        cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                    }
                }
                if (fileOutputStream != null) {
                    try {
                        fileOutputStream.close();
                    }
                    catch (IOException iOException) {
                        cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                    }
                }
            }
            ++this.cPP.cQk;
            this.cPP.Yh += n;
            this.a(cPl, apX2.bGh(), apX2.aFS(), this.cPP.cQj, l2, l);
            for (Field field : fieldArray = apX2.getClass().getDeclaredFields()) {
                Object object;
                if (!field.isAnnotationPresent(aqd.class)) continue;
                aqd aqd2 = field.getAnnotation(aqd.class);
                if (field.isAccessible()) {
                    object = field.get(apX2);
                } else {
                    field.setAccessible(true);
                    object = field.get(apX2);
                    field.setAccessible(false);
                }
                this.a(aqd2.name().hashCode(), object, apX2.aFS(), this.cPP.cQj, l2, l);
            }
            this.bGo();
        }
        catch (IOException iOException) {
            cPe.error(iOException.getMessage(), (Throwable)iOException);
        }
        catch (IllegalAccessException illegalAccessException) {
            cPe.error(illegalAccessException.getMessage(), (Throwable)illegalAccessException);
        }
    }

    private void a(apX apX2, aqi aqi2) {
        aqi aqi3 = aqi2;
        byte[] byArray = apX2.aFR();
        if (byArray == null) {
            cPe.error("Tentative de sauvegarde d'un binary storable qui n'a aucun bloc de donn\u00e9es " + String.valueOf(apX2));
            return;
        }
        if (aqi3.cQu != apX2.dy(byArray)) {
            this.b(apX2, aqi2);
            this.d(apX2);
        }
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    @Override
    protected void b(apX apX2) {
        Object object = this.cPQ;
        synchronized (object) {
            ArrayList<aqi> arrayList = this.a(cPl, apX2.aFS(), (Object)apX2.bGh(), 1);
            if (!arrayList.isEmpty()) {
                this.b(apX2, arrayList.get(0));
            }
        }
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    private void b(apX apX2, aqi aqi2) {
        this.bU(apX2.aFS(), aqi2.cQj);
        try {
            int n;
            FileInputStream fileInputStream = null;
            FilterInputStream filterInputStream = null;
            FileOutputStream fileOutputStream = null;
            try {
                this.cPR.setLength(0);
                fileInputStream = new FileInputStream(this.cPP.cQl);
                filterInputStream = this.cQe.b(fileInputStream);
                int n2 = (int)fileInputStream.getChannel().size();
                fileOutputStream = new FileOutputStream(this.cPU, false);
                fileInputStream.getChannel().position(aqi2.cQt);
                n = aqg.e((DataInputStream)filterInputStream);
                long l = aqi2.cQt + (long)n;
                fileInputStream.getChannel().transferTo(0L, aqi2.cQt, fileOutputStream.getChannel());
                fileInputStream.getChannel().transferTo(l, (long)n2 - l, fileOutputStream.getChannel());
            }
            finally {
                if (filterInputStream != null) {
                    try {
                        filterInputStream.close();
                    }
                    catch (IOException iOException) {
                        cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                    }
                }
                if (fileInputStream != null) {
                    try {
                        fileInputStream.close();
                    }
                    catch (IOException iOException) {
                        cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                    }
                }
                if (fileOutputStream != null) {
                    try {
                        fileOutputStream.close();
                    }
                    catch (IOException iOException) {
                        cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                    }
                }
            }
            this.cPR.setLength(0);
            File file = this.cPP.cQl;
            if (file.exists()) {
                file.delete();
            }
            this.cPU.renameTo(file);
            --this.cPP.cQk;
            this.cPP.Yh -= n;
            this.a(aqi2.cQj, aqi2.cQt, n, apX2);
            this.bGo();
        }
        catch (FileNotFoundException fileNotFoundException) {
            cPe.error(fileNotFoundException.getMessage(), (Throwable)fileNotFoundException);
        }
        catch (IOException iOException) {
            cPe.error(iOException.getMessage(), (Throwable)iOException);
        }
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    private void a(int n, long l, long l2, apX apX2) {
        block17: {
            try {
                int n2 = apX2.aFS();
                TIntObjectHashMap tIntObjectHashMap = (TIntObjectHashMap)this.cPK.get(n2);
                if (tIntObjectHashMap != null) {
                    TIntObjectIterator tIntObjectIterator = tIntObjectHashMap.iterator();
                    while (tIntObjectIterator.hasNext()) {
                        Object object;
                        tIntObjectIterator.advance();
                        FileOutputStream fileOutputStream = null;
                        FilterOutputStream filterOutputStream = null;
                        try {
                            fileOutputStream = new FileOutputStream(this.cPT, false);
                            filterOutputStream = this.cQf.b((OutputStream)fileOutputStream);
                            object = ((ArrayList)tIntObjectIterator.value()).iterator();
                            while (object.hasNext()) {
                                aqi aqi2 = (aqi)object.next();
                                if (aqi2.cQj == n && aqi2.cQt > l) {
                                    aqi2.cQt -= l2;
                                    aqi2.f((DataOutputStream)filterOutputStream);
                                    continue;
                                }
                                if (aqi2.cQj == n && aqi2.cQt == l) {
                                    object.remove();
                                    aqi2.aZp();
                                    continue;
                                }
                                if (n == aqi2.cQj && (n != aqi2.cQj || aqi2.cQt >= l)) continue;
                                aqi2.f((DataOutputStream)filterOutputStream);
                            }
                        }
                        finally {
                            if (filterOutputStream != null) {
                                try {
                                    filterOutputStream.close();
                                }
                                catch (IOException iOException) {
                                    cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                                }
                            }
                        }
                        object = this.bV(tIntObjectIterator.key(), n2);
                        if (((File)object).exists()) {
                            ((File)object).delete();
                        }
                        this.cPT.renameTo((File)object);
                    }
                    break block17;
                }
                cPe.error("Situation anormale : on met a jour des indexes qu'on a pas encore mont\u00e9 en memoire");
            }
            catch (IOException iOException) {
                cPe.error(iOException.getMessage(), (Throwable)iOException);
            }
        }
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     * Enabled aggressive block sorting
     * Enabled unnecessary exception pruning
     * Enabled aggressive exception aggregation
     */
    private apX[] a(ArrayList<aqi> arrayList, apX apX2) {
        if (arrayList.size() == 0) {
            return null;
        }
        ArrayList<apX> arrayList2 = new ArrayList<apX>();
        int n = apX2.aFS();
        Iterator<aqi> iterator = arrayList.iterator();
        block18: while (true) {
            if (!iterator.hasNext()) {
                if (arrayList2.size() <= 0) return null;
                return arrayList2.toArray(new apX[arrayList2.size()]);
            }
            aqi aqi2 = iterator.next();
            int n2 = aqi2.cQj;
            long l = aqi2.cQt;
            this.bU(n, n2);
            try {
                apX apX3;
                this.cPR.setLength(0);
                File file = this.cPP.cQl;
                if (!file.exists()) {
                    return null;
                }
                FileInputStream fileInputStream = null;
                FilterInputStream filterInputStream = null;
                aqg aqg2 = null;
                try {
                    fileInputStream = new FileInputStream(file);
                    filterInputStream = this.cQe.b(fileInputStream);
                    if (l < 0L) {
                        cPe.error("position n\u00e9gative");
                        apX3 = null;
                        return apX3;
                    }
                    fileInputStream.getChannel().position(l);
                    aqg2 = new aqg();
                    aqg2.d((DataInputStream)filterInputStream);
                }
                finally {
                    if (filterInputStream != null) {
                        try {
                            filterInputStream.close();
                        }
                        catch (IOException iOException) {
                            cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                        }
                    }
                    if (fileInputStream != null) {
                        try {
                            fileInputStream.close();
                        }
                        catch (IOException iOException) {
                            cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                        }
                    }
                }
                apX3 = apX2.aFN();
                ByteBuffer byteBuffer = ByteBuffer.wrap(aqg2.aKU());
                apX3.a(byteBuffer, aqg2.d(), aqg2.bGi());
                if (byteBuffer.remaining() != 0) {
                    cPe.warn("Objet restaur\u00e9 du binary storage : " + byteBuffer.remaining() + " bytes restants non lus [type:" + apX2.aFS() + " | id:" + aqg2.d() + "]");
                }
                arrayList2.add(apX3);
                Iterator iterator2 = this.cPf.iterator();
                while (true) {
                    if (!iterator2.hasNext()) continue block18;
                    aql aql2 = (aql)iterator2.next();
                    aql2.c((apS)this, apX3);
                }
            }
            catch (IOException iOException) {
                cPe.error(iOException.getMessage(), (Throwable)iOException);
                continue;
            }
            break;
        }
    }

    @Override
    public apX[] a(String string, Object object, apX apX2) {
        return this.a(string.hashCode(), object, apX2);
    }

    public apX[] a(int n, Object object, apX apX2) {
        return this.a(n, object, apX2, Integer.MAX_VALUE);
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    public apX[] a(int n, Object object, apX apX2, int n2) {
        Object object2 = this.cPQ;
        synchronized (object2) {
            return this.a(this.a(n, apX2.aFS(), object, n2), apX2);
        }
    }

    @Override
    public apX a(int n, apX apX2) {
        apX[] apXArray = this.a(cPl, (Object)n, apX2, 1);
        if (apXArray != null && apXArray.length > 0) {
            return apXArray[0];
        }
        return null;
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    @Override
    public apX[] a(apX apX2) {
        Object object = this.cPQ;
        synchronized (object) {
            ArrayList arrayList;
            TIntObjectHashMap tIntObjectHashMap = (TIntObjectHashMap)this.cPK.get(apX2.aFS());
            if (tIntObjectHashMap == null) {
                this.tA(apX2.aFS());
                tIntObjectHashMap = (TIntObjectHashMap)this.cPK.get(apX2.aFS());
            }
            if ((arrayList = (ArrayList)tIntObjectHashMap.get(cPl)) == null || arrayList.isEmpty()) {
                return null;
            }
            return this.a(arrayList, apX2);
        }
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    @Override
    public void bGd() {
        Object object = this.cPQ;
        synchronized (object) {
            File[] fileArray;
            for (File file : fileArray = this.cPW.listFiles((FilenameFilter)new aqa(this))) {
                file.delete();
            }
        }
    }

    private void bT(int n, int n2) {
        ArrayList<aqc> arrayList = (ArrayList<aqc>)this.cPJ.get(n);
        aqc aqc2 = null;
        if (arrayList == null) {
            aqc2 = new aqc(this, n, 1, 0, 0);
            arrayList = new ArrayList<aqc>();
            arrayList.add(aqc2);
            this.cPJ.put(n, arrayList);
        }
        int n3 = 0;
        for (aqc aqc3 : arrayList) {
            if (aqc3.cQj > n3) {
                n3 = aqc3.cQj;
            }
            if (aqc3.cQk + 1 > 500 || n2 + aqc3.Yh > 20000000) continue;
            aqc2 = aqc3;
            break;
        }
        if (aqc2 == null) {
            aqc2 = new aqc(this, n, n3 + 1, 0, 0);
            arrayList.add(aqc2);
        }
        this.a(aqc2);
    }

    private boolean bU(int n, int n2) {
        ArrayList<aqc> arrayList = (ArrayList<aqc>)this.cPJ.get(n);
        aqc aqc2 = null;
        if (arrayList == null) {
            aqc2 = new aqc(this, n, 1, 0, 0);
            arrayList = new ArrayList<aqc>();
            arrayList.add(aqc2);
            this.cPJ.put(n, arrayList);
        }
        for (aqc aqc3 : arrayList) {
            if (aqc3.cQj != n2) continue;
            this.a(aqc3);
            return true;
        }
        return false;
    }

    private void a(aqc aqc2) {
        this.cPP = aqc2;
    }

    private File bV(int n, int n2) {
        long l = GC.s((int)n2, (int)n);
        File file = (File)this.cPX.get(l);
        if (file != null) {
            return file;
        }
        this.cPR.setLength(0);
        String string = this.cPR.append(this.cPM).append(cQb).append(n2).append("_").append(n).append(".bdat").toString();
        file = new File(string);
        this.cPX.put(l, (Object)file);
        return file;
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    private void a(int n, Object object, int n2, int n3, long l, long l2) {
        try {
            ArrayList<aqi> arrayList;
            File file = this.bV(n, n2);
            if (!file.exists()) {
                file.createNewFile();
            }
            FileOutputStream fileOutputStream = null;
            FilterOutputStream filterOutputStream = null;
            aqi aqi2 = null;
            try {
                fileOutputStream = new FileOutputStream(file, true);
                filterOutputStream = this.cQf.b((OutputStream)fileOutputStream);
                aqi2 = aqi.a((String)object.toString(), (int)n3, (long)l, (long)l2);
                aqi2.f((DataOutputStream)filterOutputStream);
            }
            finally {
                if (filterOutputStream != null) {
                    try {
                        filterOutputStream.close();
                    }
                    catch (IOException iOException) {
                        cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                    }
                }
                if (fileOutputStream != null) {
                    try {
                        fileOutputStream.close();
                    }
                    catch (IOException iOException) {
                        cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                    }
                }
            }
            TIntObjectHashMap tIntObjectHashMap = (TIntObjectHashMap)this.cPK.get(n2);
            if (tIntObjectHashMap == null) {
                this.tA(n2);
                tIntObjectHashMap = (TIntObjectHashMap)this.cPK.get(n2);
            }
            if ((arrayList = (ArrayList<aqi>)tIntObjectHashMap.get(n)) == null) {
                arrayList = new ArrayList<aqi>(50);
                tIntObjectHashMap.put(n, arrayList);
            }
            arrayList.add(aqi2);
        }
        catch (IOException iOException) {
            cPe.error(iOException.getMessage(), (Throwable)iOException);
        }
    }

    private ArrayList<aqi> a(int n, int n2, Object object, int n3) {
        ArrayList arrayList;
        TIntObjectHashMap tIntObjectHashMap = (TIntObjectHashMap)this.cPK.get(n2);
        if (tIntObjectHashMap == null) {
            this.tA(n2);
            tIntObjectHashMap = (TIntObjectHashMap)this.cPK.get(n2);
        }
        ArrayList<aqi> arrayList2 = new ArrayList<aqi>();
        if (tIntObjectHashMap != null && (arrayList = (ArrayList)tIntObjectHashMap.get(n)) != null) {
            int n4 = arrayList.size();
            String string = object.toString();
            for (int i = 0; i < n4; ++i) {
                aqi aqi2 = (aqi)arrayList.get(i);
                if (!aqi2.cQv.equals(string)) continue;
                arrayList2.add(aqi2);
                if (arrayList2.size() >= n3) break;
            }
        }
        return arrayList2;
    }

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    private void tA(int n) {
        Pattern pattern = Pattern.compile(cQb.replaceAll("\\.", "\\\\\\.") + n + "_([a-zA-Z0-9_.-]+)" + ".bdat".replaceAll("\\.", "\\\\\\."));
        File[] fileArray = this.cPW.listFiles((FilenameFilter)new aqb(this, pattern));
        TIntObjectHashMap tIntObjectHashMap = (TIntObjectHashMap)this.cPK.get(n);
        if (tIntObjectHashMap == null) {
            tIntObjectHashMap = new TIntObjectHashMap();
            this.cPK.put(n, (Object)tIntObjectHashMap);
        }
        for (File file : fileArray) {
            int n2;
            Matcher matcher = pattern.matcher(file.getName());
            if (!matcher.matches()) continue;
            try {
                n2 = Integer.parseInt(matcher.group(1));
            }
            catch (NumberFormatException numberFormatException) {
                cPe.error("Nom de fichier d'index mal form\u00e9 : " + file.getName());
                continue;
            }
            try {
                FileInputStream fileInputStream = null;
                FilterInputStream filterInputStream = null;
                try {
                    fileInputStream = new FileInputStream(file);
                    filterInputStream = this.cQf.b(fileInputStream);
                    try {
                        while (true) {
                            aqi aqi2 = aqi.bGs();
                            aqi2.d((DataInputStream)filterInputStream);
                            ArrayList<aqi> arrayList = (ArrayList<aqi>)tIntObjectHashMap.get(n2);
                            if (arrayList == null) {
                                arrayList = new ArrayList<aqi>();
                                tIntObjectHashMap.put(n2, arrayList);
                            }
                            arrayList.add(aqi2);
                        }
                    }
                    catch (EOFException eOFException) {
                        if (filterInputStream != null) {
                            try {
                                filterInputStream.close();
                            }
                            catch (IOException iOException) {
                                cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                            }
                        }
                        if (fileInputStream == null) continue;
                        try {
                            fileInputStream.close();
                        }
                        catch (IOException iOException) {
                            cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                        }
                    }
                }
                catch (Throwable throwable) {
                    if (filterInputStream != null) {
                        try {
                            filterInputStream.close();
                        }
                        catch (IOException iOException) {
                            cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                        }
                    }
                    if (fileInputStream != null) {
                        try {
                            fileInputStream.close();
                        }
                        catch (IOException iOException) {
                            cPe.error("Impossible de fermer le descripteur ouvert sur un fichier !", (Throwable)iOException);
                        }
                    }
                    throw throwable;
                }
            }
            catch (FileNotFoundException fileNotFoundException) {
                cPe.error(fileNotFoundException.getMessage());
            }
            catch (IOException iOException) {
                cPe.error(iOException.getMessage());
            }
        }
    }

    @Override
    public String toString() {
        return "BinaryStorage working under " + this.cPM;
    }
}
